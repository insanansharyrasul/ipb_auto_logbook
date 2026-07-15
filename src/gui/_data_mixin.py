"""Logbook Data tab — editable CSV table with toolbar."""

from __future__ import annotations

from tkinter import filedialog
from typing import Any

import customtkinter as ctk
import pandas as pd

from src.automator import resolve_to_absolute_path
from src.gui._constants import BERITA_VALUES, CSV_COLUMNS, TIPE_VALUES


class DataTabMixin:
    """Mixin that builds the Logbook Data tab and its table logic."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_data_tab(self) -> None:
        parent = self._tab_data

        # -- toolbar --------------------------------------------------------
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(10, 4))

        ctk.CTkButton(
            toolbar,
            text="Load CSV from config",
            width=100,
            command=self._load_csv,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(toolbar, text="Add Row", width=90, command=self._add_row).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(
            toolbar, text="Delete Last", width=100, command=self._delete_last_row
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(toolbar, text="Save CSV", width=90, command=self._save_csv).pack(
            side="left"
        )

        # -- header row -----------------------------------------------------
        header_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", padx=10, pady=(6, 0))
        col_widths = [10, 7, 7, 14, 8, 5, 10, 8]
        for idx, col_name in enumerate(CSV_COLUMNS):
            lbl = ctk.CTkLabel(
                header_frame,
                text=col_name.capitalize(),
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=4)
            header_frame.grid_columnconfigure(idx, weight=col_widths[idx])

        # -- scrollable body ------------------------------------------------
        self._table_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self._table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._table_frame.grid_columnconfigure(list(range(8)), weight=1)

        self._table_rows.clear()

    # ------------------------------------------------------------------
    # Row widget factory
    # ------------------------------------------------------------------

    def _make_row_widgets(
        self, parent_frame: ctk.CTkFrame, row_idx: int
    ) -> dict[str, Any]:
        widgets: dict[str, Any] = {}
        col = 0

        # tanggal
        w = ctk.CTkEntry(parent_frame, width=90, placeholder_text="")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["tanggal"] = w
        col += 1

        # mulai
        w = ctk.CTkEntry(parent_frame, width=65, placeholder_text="")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["mulai"] = w
        col += 1

        # selesai
        w = ctk.CTkEntry(parent_frame, width=65, placeholder_text="")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["selesai"] = w
        col += 1

        # keterangan
        w = ctk.CTkEntry(parent_frame, placeholder_text="")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["keterangan"] = w
        col += 1

        # file + browse button
        file_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        file_frame.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        file_frame.grid_columnconfigure(0, weight=1)
        w_file = ctk.CTkEntry(file_frame, placeholder_text="")
        w_file.grid(row=0, column=0, sticky="ew")
        btn = ctk.CTkButton(
            file_frame,
            text="...",
            width=32,
            height=28,
            command=lambda e=w_file: self._browse_file_cell(e),
        )
        btn.grid(row=0, column=1, padx=(2, 0))
        widgets["file"] = w_file
        col += 1

        # tipe
        w = ctk.CTkComboBox(parent_frame, values=TIPE_VALUES, width=90)
        w.set("offline")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["tipe"] = w
        col += 1

        # lokasi
        w = ctk.CTkEntry(parent_frame, placeholder_text="")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["lokasi"] = w
        col += 1

        # berita
        w = ctk.CTkComboBox(parent_frame, values=BERITA_VALUES, width=105)
        w.set("kegiatan")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["berita"] = w

        return widgets

    # ------------------------------------------------------------------
    # Row helpers
    # ------------------------------------------------------------------

    def _browse_file_cell(self, entry_widget: ctk.CTkEntry) -> None:
        path = filedialog.askopenfilename(title="Select file")
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _clear_table(self) -> None:
        for row_data in self._table_rows:
            for w in row_data.values():
                w.destroy()
        self._table_rows.clear()

    def _populate_table(self, df: pd.DataFrame) -> None:
        self._clear_table()
        for i in range(df.shape[0]):
            row_data = self._make_row_widgets(self._table_frame, i)
            for col_name in CSV_COLUMNS:
                value = str(df[col_name].iloc[i]) if col_name in df.columns else ""
                widget = row_data[col_name]
                if isinstance(widget, ctk.CTkEntry):
                    widget.insert(0, value)
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set(value)
            self._table_rows.append(row_data)

    def _ensure_min_rows(self) -> None:
        while len(self._table_rows) < 3:
            self._add_row()

    def _add_row(self) -> None:
        idx = len(self._table_rows)
        row_data = self._make_row_widgets(self._table_frame, idx)
        if isinstance(row_data["tipe"], ctk.CTkComboBox):
            row_data["tipe"].set("offline")
        if isinstance(row_data["berita"], ctk.CTkComboBox):
            row_data["berita"].set("kegiatan")
        self._table_rows.append(row_data)

    def _delete_last_row(self) -> None:
        if not self._table_rows:
            return
        row_data = self._table_rows.pop()
        for w in row_data.values():
            w.destroy()

    def _gather_table_data(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for row_data in self._table_rows:
            entry: dict[str, str] = {}
            for col_name in CSV_COLUMNS:
                w = row_data[col_name]
                if isinstance(w, ctk.CTkEntry):
                    entry[col_name] = w.get().strip()
                elif isinstance(w, ctk.CTkComboBox):
                    entry[col_name] = w.get().strip()
            rows.append(entry)
        return rows

    # ------------------------------------------------------------------
    # CSV I/O
    # ------------------------------------------------------------------

    def _load_csv(self) -> None:
        path = self._ent_csv.get().strip()
        if not path:
            path = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
            if path:
                self._ent_csv.delete(0, "end")
                self._ent_csv.insert(0, path)
        if not path:
            return

        try:
            abs_path = resolve_to_absolute_path(path)
            df = pd.read_csv(abs_path)
            self._populate_table(df)
            self._ensure_min_rows()
            self._log(f"Loaded {df.shape[0]} rows from {path}")
        except Exception as e:
            self._log(f"Failed to load CSV: {e}")

    def _save_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            data = self._gather_table_data()
            df = pd.DataFrame(data, columns=CSV_COLUMNS)
            df.to_csv(path, index=False)
            self._log(f"Saved {len(data)} rows to {path}")
        except Exception as e:
            self._log(f"Failed to save CSV: {e}")
