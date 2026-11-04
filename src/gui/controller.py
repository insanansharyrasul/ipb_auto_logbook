"""QtQuick-facing controller and logbook row model."""

from __future__ import annotations

import csv
from dataclasses import asdict, replace
from datetime import datetime

from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QThread,
    Qt,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtWidgets import QFileDialog

from src.automator import (
    CSV_COLUMNS,
    LogbookAutomator,
    LogbookConfig,
    resolve_to_absolute_path,
)

_ROLE0 = int(Qt.ItemDataRole.UserRole)
_DEFAULTS = {"tipe": "offline", "berita": "kegiatan"}
_CSV_FILTERS = ["CSV files (*.csv)", "All files (*)"]
_JSON_FILTERS = ["JSON files (*.json)", "All files (*)"]


def _normalized(row: dict) -> dict[str, str]:
    """A row with every CSV column, blank tipe/berita filled with defaults."""
    return {c: str(row.get(c) or _DEFAULTS.get(c, "")) for c in CSV_COLUMNS}


class LogbookRowsModel(QAbstractListModel):
    """Editable list of CSV rows, one role per column."""

    countChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict[str, str]] = []

    # -- QAbstractListModel ------------------------------------------------

    def roleNames(self) -> dict[int, bytes]:  # noqa: N802 (Qt override)
        return {_ROLE0 + i: name.encode() for i, name in enumerate(CSV_COLUMNS)}

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def data(self, index: QModelIndex, role: int = 0):
        col = role - _ROLE0
        if index.isValid() and 0 <= col < len(CSV_COLUMNS):
            return self._rows[index.row()][CSV_COLUMNS[col]]
        return None

    # -- QML API -----------------------------------------------------------

    @pyqtProperty(int, notify=countChanged)
    def count(self) -> int:
        return len(self._rows)

    @pyqtSlot(int, str, str)
    def setField(self, row: int, column: str, value: str) -> None:  # noqa: N802
        if column not in CSV_COLUMNS or not 0 <= row < len(self._rows):
            return
        self._rows[row][column] = value
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [_ROLE0 + CSV_COLUMNS.index(column)])

    @pyqtSlot()
    def addRow(self) -> None:  # noqa: N802
        self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
        self._rows.append(_normalized({}))
        self.endInsertRows()
        self.countChanged.emit()

    @pyqtSlot()
    def removeLastRow(self) -> None:  # noqa: N802
        if not self._rows:
            return
        last = len(self._rows) - 1
        self.beginRemoveRows(QModelIndex(), last, last)
        self._rows.pop()
        self.endRemoveRows()
        self.countChanged.emit()

    # -- Python API --------------------------------------------------------

    def load(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = [_normalized(row) for row in rows]
        self.endResetModel()
        self.countChanged.emit()

    def to_rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self._rows]


class _RunWorker(QThread):
    """Runs the automator off the UI thread, relaying its callbacks as signals."""

    progress = pyqtSignal(int, int, str)
    log = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, config: LogbookConfig) -> None:
        super().__init__()
        self.automator = LogbookAutomator(
            config=config,
            progress_callback=self.progress.emit,
            log_callback=self.log.emit,
        )

    def run(self) -> None:
        try:
            self.done.emit(self.automator.run())
        except Exception as exc:  # pragma: no cover - defensive thread boundary
            self.log.emit(f"✗ Fatal error: {exc}")
            self.done.emit(False)


def _config_prop(type_, field: str, notify):
    """Read/write Qt property backed by one LogbookConfig field."""

    def fset(self: AppController, value) -> None:
        if getattr(self._config, field) != value:
            setattr(self._config, field, value)
            self.configChanged.emit()

    return pyqtProperty(type_, lambda self: getattr(self._config, field), fset, notify=notify)


class AppController(QObject):
    """Exposes configuration, CSV data, and run state to the QML UI."""

    configChanged = pyqtSignal()
    runningChanged = pyqtSignal()
    stoppingChanged = pyqtSignal()
    statusTextChanged = pyqtSignal()
    statusKindChanged = pyqtSignal()
    progressChanged = pyqtSignal()
    logTextChanged = pyqtSignal()

    username = _config_prop(str, "username", configChanged)
    password = _config_prop(str, "password", configChanged)
    dosen = _config_prop(str, "dosen", configChanged)
    rowNumber = _config_prop(str, "row_number", configChanged)
    semester = _config_prop(str, "semester", configChanged)
    csvPath = _config_prop(str, "csv_path", configChanged)
    headless = _config_prop(bool, "headless", configChanged)
    slowMo = _config_prop(int, "slow_mo", configChanged)

    def __init__(self) -> None:
        super().__init__()
        self._config = LogbookConfig()
        self._running = False
        self._stopping = False
        self._status_text = "Ready"
        self._status_kind = "idle"
        self._progress_current = 0
        self._progress_total = 0
        self._log_text = ""
        self._worker: _RunWorker | None = None
        self._rows_model = LogbookRowsModel()

    @pyqtProperty(QObject, constant=True)
    def rows(self) -> LogbookRowsModel:
        return self._rows_model

    # ------------------------------------------------------------------
    # Run state
    # ------------------------------------------------------------------

    @pyqtProperty(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @pyqtProperty(bool, notify=stoppingChanged)
    def stopping(self) -> bool:
        return self._stopping

    @pyqtProperty(str, notify=statusTextChanged)
    def statusText(self) -> str:
        return self._status_text

    @pyqtProperty(str, notify=statusKindChanged)
    def statusKind(self) -> str:
        return self._status_kind

    @pyqtProperty(int, notify=progressChanged)
    def progressCurrent(self) -> int:
        return self._progress_current

    @pyqtProperty(int, notify=progressChanged)
    def progressTotal(self) -> int:
        return self._progress_total

    @pyqtProperty(str, notify=logTextChanged)
    def logText(self) -> str:
        return self._log_text

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    # QML's FileDialog needs the Qt.labs.folderlistmodel module, which the
    # PyQt6 wheel does not ship, so file pickers use the QtWidgets dialog.
    def _choose_file(self, title: str, filters: list[str], save_suffix: str = "") -> str:
        """Local path the user picked, or "" if cancelled. save_suffix makes it a save dialog."""
        dialog = QFileDialog(None, title)
        dialog.setNameFilters(filters)
        if save_suffix:
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setDefaultSuffix(save_suffix)
        if dialog.exec() != QFileDialog.DialogCode.Accepted:
            return ""
        return next(iter(dialog.selectedFiles()), "")

    @pyqtSlot()
    def chooseCsvFile(self) -> None:
        if path := self._choose_file("Select CSV file", _CSV_FILTERS):
            self.csvPath = path

    @pyqtSlot()
    def chooseSaveConfig(self) -> None:
        if not (path := self._choose_file("Save config", _JSON_FILTERS, "json")):
            return
        try:
            self._gather_config().save_to_file(path)
            self._log(f"Saved config to {path} (password excluded)")
        except Exception as exc:
            self._log(f"Failed to save config: {exc}")

    @pyqtSlot()
    def chooseLoadConfig(self) -> None:
        if not (path := self._choose_file("Load config", _JSON_FILTERS)):
            return
        try:
            self._config = LogbookConfig.load_from_file(path)  # password blank
            self.configChanged.emit()
            self._log(f"Loaded config from {path} (re-enter password)")
        except Exception as exc:
            self._log(f"Failed to load config: {exc}")

    @pyqtSlot()
    def chooseLoadCsv(self) -> None:
        if path := self._choose_file("Select CSV file", _CSV_FILTERS):
            self.csvPath = path
            self.loadCsv()

    @pyqtSlot()
    def chooseSaveCsv(self) -> None:
        if not (path := self._choose_file("Save CSV", _CSV_FILTERS, "csv")):
            return
        try:
            data = self._rows_model.to_rows()
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(data)
            self._log(f"Saved {len(data)} rows to {path}")
        except Exception as exc:
            self._log(f"Failed to save CSV: {exc}")

    @pyqtSlot(int)
    def chooseRowFile(self, row: int) -> None:
        if path := self._choose_file("Select file", ["All files (*)"]):
            self._rows_model.setField(row, "file", path)

    @pyqtSlot()
    def loadCsv(self) -> None:
        path = self._config.csv_path.strip()
        if not path:
            self._log("⚠ No CSV file selected.")
            return
        try:
            with open(resolve_to_absolute_path(path), newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self._rows_model.load(rows)
            while self._rows_model.count < 3:
                self._rows_model.addRow()
            self._log(f"Loaded {len(rows)} rows from {path}")
        except Exception as exc:
            self._log(f"Failed to load CSV: {exc}")

    # ------------------------------------------------------------------
    # Automation actions
    # ------------------------------------------------------------------

    @pyqtSlot()
    def start(self) -> None:
        if self._running:
            return
        config = self._gather_config()
        if not config.username or not config.password:
            self._log("⚠ Username and password are required.")
            return

        self._worker = _RunWorker(config)
        self._worker.progress.connect(self._on_progress)
        self._worker.log.connect(self._append_log)
        self._worker.done.connect(self._on_done)

        self._set_running(True)
        self._clear_log()
        self._log(f"Starting automation with {config.csv_path}...")
        self._worker.start()

    @pyqtSlot()
    def stop(self) -> None:
        if self._worker is None or not self._worker.isRunning():
            return
        self._worker.automator.stop()
        self._stopping = True
        self.stoppingChanged.emit()
        self._set_status("Stopping...", "running")

    @pyqtSlot()
    def shutdown(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.automator.stop()
            self._worker.wait(3000)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _gather_config(self) -> LogbookConfig:
        """Current config with surrounding whitespace stripped from text fields."""
        c = self._config
        return replace(c, **{k: v.strip() for k, v in asdict(c).items() if isinstance(v, str)})

    def _set_running(self, running: bool) -> None:
        self._running = running
        self._stopping = False
        self.runningChanged.emit()
        self.stoppingChanged.emit()
        if running:
            self._set_status("Running...", "running")
        else:
            self._set_status("Ready", "idle")

    def _set_status(self, text: str, kind: str) -> None:
        if self._status_text != text:
            self._status_text = text
            self.statusTextChanged.emit()
        if self._status_kind != kind:
            self._status_kind = kind
            self.statusKindChanged.emit()

    def _on_progress(self, current: int, total: int, message: str) -> None:
        self._progress_current = current
        self._progress_total = total
        self.progressChanged.emit()
        self._log(message)

    def _on_done(self, success: bool) -> None:
        self._set_running(False)
        if success:
            self._progress_current = self._progress_total or 1
            self._progress_total = self._progress_total or 1
            self._set_status("Completed ✓", "success")
        else:
            self._set_status("Failed ✗", "error")
        self.progressChanged.emit()
        self._worker = None

    def _clear_log(self) -> None:
        self._log_text = ""
        self.logTextChanged.emit()

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self._append_log(f"[{stamp}] {message}")

    def _append_log(self, message: str) -> None:
        self._log_text += f"{message}\n"
        self.logTextChanged.emit()
