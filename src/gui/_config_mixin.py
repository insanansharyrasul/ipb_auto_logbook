"""Configuration tab — account, logbook params, CSV source, options."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.automator import LogbookConfig
from src.gui._constants import DOSEN_INFO, ROW_NUMBER_INFO, SEMESTER_INFO


def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
    return lbl


class ConfigTabMixin:
    """Mixin that builds the Configuration tab and its helpers."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_config_tab(self) -> None:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(4)

        # --- Account -----------------------------------------------------
        root.addWidget(_section("Account"))
        account = QFormLayout()
        self._ent_username = QLineEdit()
        self._ent_password = QLineEdit()
        self._ent_password.setEchoMode(QLineEdit.EchoMode.Password)
        account.addRow("Username", self._ent_username)
        account.addRow("Password", self._ent_password)
        root.addLayout(account)

        # --- Logbook -----------------------------------------------------
        root.addWidget(_section("Logbook"))
        logbook = QFormLayout()
        self._ent_dosen = QLineEdit()
        self._ent_row = QLineEdit()
        self._ent_semester = QLineEdit()
        logbook.addRow(self._make_label_with_info("Dosen", DOSEN_INFO), self._ent_dosen)
        logbook.addRow(
            self._make_label_with_info("Row Number", ROW_NUMBER_INFO), self._ent_row
        )
        logbook.addRow(
            self._make_label_with_info("Semester", SEMESTER_INFO), self._ent_semester
        )
        root.addLayout(logbook)

        # --- Data Source -------------------------------------------------
        root.addWidget(_section("Data Source"))
        self._ent_csv = QLineEdit("data.csv")
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse_csv)
        csv_row = QHBoxLayout()
        csv_row.addWidget(self._ent_csv, 1)
        csv_row.addWidget(browse)
        data_form = QFormLayout()
        data_form.addRow("CSV File", csv_row)
        root.addLayout(data_form)

        # --- Options -----------------------------------------------------
        root.addWidget(_section("Options"))
        self._chk_headless = QCheckBox("Headless (no browser window)")
        root.addWidget(self._chk_headless)

        self._spin_slowmo = QSpinBox()
        self._spin_slowmo.setRange(50, 500)
        self._spin_slowmo.setSingleStep(50)
        self._spin_slowmo.setValue(200)
        slowmo_form = QFormLayout()
        slowmo_form.addRow("Slow Mo (ms)", self._spin_slowmo)
        root.addLayout(slowmo_form)

        # --- Config file -------------------------------------------------
        cfg_btns = QHBoxLayout()
        btn_save = QPushButton("Save Config")
        btn_save.clicked.connect(self._save_config)
        btn_load = QPushButton("Load Config")
        btn_load.clicked.connect(self._load_config)
        cfg_btns.addWidget(btn_save)
        cfg_btns.addWidget(btn_load)
        cfg_btns.addStretch(1)
        root.addSpacing(10)
        root.addLayout(cfg_btns)

        root.addStretch(1)
        self._tabview.addTab(page, "Configuration")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gather_config(self) -> LogbookConfig:
        return LogbookConfig(
            username=self._ent_username.text().strip(),
            password=self._ent_password.text().strip(),
            dosen=self._ent_dosen.text().strip(),
            row_number=self._ent_row.text().strip(),
            semester=self._ent_semester.text().strip(),
            csv_path=self._ent_csv.text().strip(),
            headless=self._chk_headless.isChecked(),
            slow_mo=self._spin_slowmo.value(),
        )

    def _browse_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV file", "", "CSV files (*.csv);;All files (*)"
        )
        if path:
            self._ent_csv.setText(path)

    def _save_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save config", "config.json", "JSON files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            self._gather_config().save_to_file(path)
            self._log(f"Saved config to {path} (password excluded)")
        except Exception as e:
            self._log(f"Failed to save config: {e}")

    def _load_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load config", "", "JSON files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            self._apply_config(LogbookConfig.load_from_file(path))
            self._log(f"Loaded config from {path} (re-enter password)")
        except Exception as e:
            self._log(f"Failed to load config: {e}")

    def _apply_config(self, cfg: LogbookConfig) -> None:
        self._ent_username.setText(cfg.username)
        self._ent_password.setText(cfg.password)  # blank — not saved to disk
        self._ent_dosen.setText(cfg.dosen)
        self._ent_row.setText(cfg.row_number)
        self._ent_semester.setText(cfg.semester)
        self._ent_csv.setText(cfg.csv_path)
        self._chk_headless.setChecked(cfg.headless)
        self._spin_slowmo.setValue(cfg.slow_mo)
