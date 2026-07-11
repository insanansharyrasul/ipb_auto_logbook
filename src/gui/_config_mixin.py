"""Configuration tab — account, logbook params, CSV source, options."""

from __future__ import annotations

from tkinter import filedialog

import customtkinter as ctk

from src.automator import LogbookConfig
from src.gui._constants import DOSEN_INFO, ROW_NUMBER_INFO, SEMESTER_INFO


class ConfigTabMixin:
    """Mixin that builds the Configuration tab and its helpers."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_config_tab(self) -> None:
        parent = self._tab_config
        parent.grid_columnconfigure(1, weight=1)

        row = 0
        pad = {"padx": 10, "pady": 6, "sticky": "w"}

        # --- Account -----------------------------------------------------
        ctk.CTkLabel(
            parent, text="Account", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="w")
        row += 1

        ctk.CTkLabel(parent, text="Username").grid(row=row, column=0, **pad)
        self._ent_username = ctk.CTkEntry(parent, width=280, placeholder_text="")
        self._ent_username.grid(row=row, column=1, **pad)
        row += 1

        ctk.CTkLabel(parent, text="Password").grid(row=row, column=0, **pad)
        self._ent_password = ctk.CTkEntry(
            parent, width=280, show="*", placeholder_text=""
        )
        self._ent_password.grid(row=row, column=1, **pad)
        row += 1

        # --- Logbook -----------------------------------------------------
        ctk.CTkLabel(
            parent, text="Logbook", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        self._make_label_with_info(parent, "Dosen", DOSEN_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_dosen = ctk.CTkEntry(parent, width=400, placeholder_text="")
        self._ent_dosen.grid(row=row, column=1, **pad)
        row += 1

        self._make_label_with_info(parent, "Row Number", ROW_NUMBER_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_row = ctk.CTkEntry(parent, width=120, placeholder_text="")
        self._ent_row.grid(row=row, column=1, **pad)
        row += 1

        self._make_label_with_info(parent, "Semester", SEMESTER_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_semester = ctk.CTkEntry(parent, width=400, placeholder_text="")
        self._ent_semester.grid(row=row, column=1, **pad)
        row += 1

        # --- Data Source -------------------------------------------------
        ctk.CTkLabel(
            parent, text="Data Source", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        ctk.CTkLabel(parent, text="CSV File").grid(row=row, column=0, **pad)
        csv_frame = ctk.CTkFrame(parent, fg_color="transparent")
        csv_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=6)
        csv_frame.grid_columnconfigure(0, weight=1)
        self._ent_csv = ctk.CTkEntry(csv_frame, placeholder_text="")
        self._ent_csv.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._ent_csv.insert(0, "data.csv")
        ctk.CTkButton(
            csv_frame, text="Browse", width=80, command=self._browse_csv
        ).grid(row=0, column=1)
        row += 1

        # --- Options -----------------------------------------------------
        ctk.CTkLabel(
            parent, text="Options", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        self._var_headless = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            parent,
            text="Headless (no browser window)",
            variable=self._var_headless,
        ).grid(row=row, column=1, **pad)
        row += 1

        ctk.CTkLabel(parent, text="Slow Mo (ms)").grid(row=row, column=0, **pad)
        spin_frame = ctk.CTkFrame(parent, fg_color="transparent")
        spin_frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        self._var_slowmo = ctk.StringVar(value="200")
        ctk.CTkEntry(
            spin_frame,
            width=80,
            textvariable=self._var_slowmo,
            placeholder_text="",
        ).pack(side="left")
        ctk.CTkLabel(spin_frame, text="(50–500)").pack(side="left", padx=6)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gather_config(self) -> LogbookConfig:
        slow_mo_str = self._var_slowmo.get().strip()
        try:
            slow_mo = int(slow_mo_str)
        except ValueError:
            slow_mo = 200
        slow_mo = max(50, min(500, slow_mo))

        return LogbookConfig(
            username=self._ent_username.get().strip(),
            password=self._ent_password.get().strip(),
            dosen=self._ent_dosen.get().strip(),
            row_number=self._ent_row.get().strip(),
            semester=self._ent_semester.get().strip(),
            csv_path=self._ent_csv.get().strip(),
            headless=self._var_headless.get(),
            slow_mo=slow_mo,
        )

    def _browse_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self._ent_csv.delete(0, "end")
            self._ent_csv.insert(0, path)
