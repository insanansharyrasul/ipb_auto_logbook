"""Logbook Data tab — editable CSV table with toolbar."""

from __future__ import annotations

import csv
from typing import Any

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.automator import resolve_to_absolute_path
from src.gui._constants import BERITA_VALUES, CSV_COLUMNS, TIPE_VALUES

# relative column stretch factors (matches the old grid weights)
_COL_STRETCH = [10, 7, 7, 14, 8, 5, 10, 8]


class DataTabMixin:
    """Mixin that builds the Logbook Data tab and its table logic."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_data_tab(self) -> None:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(10, 10, 10, 10)

        # -- toolbar --------------------------------------------------------
        toolbar = QHBoxLayout()
        for text, handler in (
            ("Load CSV from config", self._load_csv),
            ("Add Row", self._add_row),
            ("Delete Last", self._delete_last_row),
            ("Save CSV", self._save_csv),
        ):
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            toolbar.addWidget(btn)
        toolbar.addStretch(1)
        root.addLayout(toolbar)

        # -- scrollable grid (header row + data rows share one grid) --------
        container = QWidget()
        self._table_grid = QGridLayout(container)
        self._table_grid.setContentsMargins(0, 0, 0, 0)
        self._table_grid.setHorizontalSpacing(4)
        self._table_grid.setVerticalSpacing(2)
        for idx, col_name in enumerate(CSV_COLUMNS):
            header = QLabel(col_name.capitalize())
            header.setStyleSheet("font-weight: bold;")
            self._table_grid.addWidget(header, 0, idx)
            self._table_grid.setColumnStretch(idx, _COL_STRETCH[idx])
        self._table_grid.setRowStretch(1000, 1)  # keep rows top-aligned

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        self._table_rows.clear()
        self._tabview.addTab(page, "Logbook Data")

    # ------------------------------------------------------------------
    # Row widget factory
    # ------------------------------------------------------------------

    def _make_row_widgets(self, grid_row: int) -> dict[str, Any]:
        widgets: dict[str, Any] = {}
        cells: list[QWidget] = []

        def place(col: int, w: QWidget) -> None:
            self._table_grid.addWidget(w, grid_row, col)
            cells.append(w)

        # plain text columns
        for col, name in (
            (0, "tanggal"),
            (1, "mulai"),
            (2, "selesai"),
            (3, "keterangan"),
        ):
            w = QLineEdit()
            place(col, w)
            widgets[name] = w

        # file + browse button (container is the grid cell; entry holds value)
        file_container = QWidget()
        file_lay = QHBoxLayout(file_container)
        file_lay.setContentsMargins(0, 0, 0, 0)
        file_lay.setSpacing(2)
        w_file = QLineEdit()
        btn = QPushButton("...")
        btn.setFixedWidth(32)
        btn.clicked.connect(lambda _=False, e=w_file: self._browse_file_cell(e))
        file_lay.addWidget(w_file, 1)
        file_lay.addWidget(btn)
        place(4, file_container)
        widgets["file"] = w_file

        # tipe combobox
        w_tipe = QComboBox()
        w_tipe.addItems(TIPE_VALUES)
        w_tipe.setCurrentText("offline")
        place(5, w_tipe)
        widgets["tipe"] = w_tipe

        # lokasi
        w_lokasi = QLineEdit()
        place(6, w_lokasi)
        widgets["lokasi"] = w_lokasi

        # berita combobox
        w_berita = QComboBox()
        w_berita.addItems(BERITA_VALUES)
        w_berita.setCurrentText("kegiatan")
        place(7, w_berita)
        widgets["berita"] = w_berita

        widgets["_cells"] = cells
        return widgets

    # ------------------------------------------------------------------
    # Row helpers
    # ------------------------------------------------------------------

    def _browse_file_cell(self, entry_widget: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            entry_widget.setText(path)

    def _clear_table(self) -> None:
        for row_data in self._table_rows:
            for w in row_data["_cells"]:
                w.deleteLater()
        self._table_rows.clear()

    def _populate_table(self, rows: list[dict[str, str]]) -> None:
        self._clear_table()
        for i, row in enumerate(rows):
            row_data = self._make_row_widgets(grid_row=i + 1)  # row 0 is the header
            for col_name in CSV_COLUMNS:
                value = str(row.get(col_name) or "")
                widget = row_data[col_name]
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
            self._table_rows.append(row_data)

    def _ensure_min_rows(self) -> None:
        while len(self._table_rows) < 3:
            self._add_row()

    def _add_row(self) -> None:
        row_data = self._make_row_widgets(grid_row=len(self._table_rows) + 1)
        self._table_rows.append(row_data)

    def _delete_last_row(self) -> None:
        if not self._table_rows:
            return
        row_data = self._table_rows.pop()
        for w in row_data["_cells"]:
            w.deleteLater()

    def _gather_table_data(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for row_data in self._table_rows:
            entry: dict[str, str] = {}
            for col_name in CSV_COLUMNS:
                w = row_data[col_name]
                if isinstance(w, QLineEdit):
                    entry[col_name] = w.text().strip()
                elif isinstance(w, QComboBox):
                    entry[col_name] = w.currentText().strip()
            rows.append(entry)
        return rows

    # ------------------------------------------------------------------
    # CSV I/O
    # ------------------------------------------------------------------

    def _load_csv(self) -> None:
        path = self._ent_csv.text().strip()
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select CSV file", "", "CSV files (*.csv);;All files (*)"
            )
            if path:
                self._ent_csv.setText(path)
        if not path:
            return

        try:
            abs_path = resolve_to_absolute_path(path)
            with open(abs_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self._populate_table(rows)
            self._ensure_min_rows()
            self._log(f"Loaded {len(rows)} rows from {path}")
        except Exception as e:
            self._log(f"Failed to load CSV: {e}")

    def _save_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "data.csv", "CSV files (*.csv);;All files (*)"
        )
        if not path:
            return
        try:
            data = self._gather_table_data()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(data)
            self._log(f"Saved {len(data)} rows to {path}")
        except Exception as e:
            self._log(f"Failed to save CSV: {e}")
