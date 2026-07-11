"""IPB Auto Logbook — Desktop GUI (CustomTkinter).

Launch with:  python gui_app.py
"""

from __future__ import annotations

import queue
import sys
import threading
import time
from datetime import datetime
from tkinter import filedialog
from typing import Any, Optional

try:
    import customtkinter as ctk
except ImportError:
    print(
        "customtkinter is not installed.\n"
        "Install it with:  pip install customtkinter"
    )
    sys.exit(1)

import pandas as pd

from src.automator import (
    LogbookAutomator,
    LogbookConfig,
    LogbookRow,  # noqa: F401
    resolve_to_absolute_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIPE_VALUES: list[str] = ["offline", "online", "hybrid"]
BERITA_VALUES: list[str] = ["kegiatan", "ujian", "bimbingan"]
CSV_COLUMNS: list[str] = [
    "tanggal",
    "mulai",
    "selesai",
    "keterangan",
    "file",
    "tipe",
    "lokasi",
    "berita",
]

# Info tooltips for configuration fields
DOSEN_INFO: str = (
    "Nama Dosen Penggerak dari Student Portal.\n"
    "Kemahasiswaan → Aktivitas → Log (ikon list) → Tambah.\n"
    "Contoh: 'Jeffrey Einstein, S.Komp., Ph.D.'."
)
ROW_NUMBER_INFO: str = (
    "Angka di kolom 'No' pada halaman Kemahasiswaan → Aktivitas."
)
SEMESTER_INFO: str = (
    "Tahun & semester sesuai kolom 'Tahun Semester'.\n"
    "Contoh: '2026/2027 Semester Genap'."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ===================================================================
# Main Application
# ===================================================================


class LogbookApp(ctk.CTk):
    """Root application window."""

    def __init__(self) -> None:
        super().__init__()

        # -- window ------------------------------------------------------------------
        self.title("IPB Auto Logbook")
        self.geometry("900x700")
        self.minsize(800, 600)

        # appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # -- state -------------------------------------------------------------------
        self._automator: Optional[LogbookAutomator] = None
        self._thread: Optional[threading.Thread] = None
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._table_rows: list[dict[str, Any]] = []  # widget refs per data row

        # -- build UI ----------------------------------------------------------------
        self._build_tabview()
        self._build_config_tab()
        self._build_data_tab()
        self._build_run_tab()

        # -- close handling ----------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # start queue polling
        self._poll_queue()

    # =======================================================================
    # Tab View
    # =======================================================================

    def _build_tabview(self) -> None:
        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_config = self._tabview.add("Configuration")
        self._tab_data = self._tabview.add("Logbook Data")
        self._tab_run = self._tabview.add("Run")

        self._tabview.set("Configuration")

    # =======================================================================
    # Tab 1 — Configuration
    # =======================================================================

    def _build_config_tab(self) -> None:
        parent = self._tab_config
        parent.grid_columnconfigure(1, weight=1)

        row = 0
        pad = {"padx": 10, "pady": 6, "sticky": "w"}

        # --- section label ----------------------------------------------------------
        ctk.CTkLabel(
            parent, text="Account", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="w")
        row += 1

        # Username
        ctk.CTkLabel(parent, text="Username").grid(row=row, column=0, **pad)
        self._ent_username = ctk.CTkEntry(parent, width=280)
        self._ent_username.grid(row=row, column=1, **pad)
        row += 1

        # Password
        ctk.CTkLabel(parent, text="Password").grid(row=row, column=0, **pad)
        self._ent_password = ctk.CTkEntry(parent, width=280, show="*")
        self._ent_password.grid(row=row, column=1, **pad)
        row += 1

        # --- section label ----------------------------------------------------------
        ctk.CTkLabel(
            parent, text="Logbook", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        # Dosen
        self._make_label_with_info(parent, "Dosen", DOSEN_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_dosen = ctk.CTkEntry(parent, width=400)
        self._ent_dosen.grid(row=row, column=1, **pad)
        row += 1

        # Row Number
        self._make_label_with_info(parent, "Row Number", ROW_NUMBER_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_row = ctk.CTkEntry(parent, width=120)
        self._ent_row.grid(row=row, column=1, **pad)
        row += 1

        # Semester
        self._make_label_with_info(parent, "Semester", SEMESTER_INFO).grid(
            row=row, column=0, **pad
        )
        self._ent_semester = ctk.CTkEntry(parent, width=400)
        self._ent_semester.grid(row=row, column=1, **pad)
        row += 1

        # --- section label ----------------------------------------------------------
        ctk.CTkLabel(
            parent, text="Data Source", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        # CSV Path
        ctk.CTkLabel(parent, text="CSV File").grid(row=row, column=0, **pad)
        csv_frame = ctk.CTkFrame(parent, fg_color="transparent")
        csv_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=6)
        csv_frame.grid_columnconfigure(0, weight=1)
        self._ent_csv = ctk.CTkEntry(csv_frame)
        self._ent_csv.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._ent_csv.insert(0, "data.csv")
        ctk.CTkButton(
            csv_frame, text="Browse", width=80, command=self._browse_csv
        ).grid(row=0, column=1)
        row += 1

        # --- section label ----------------------------------------------------------
        ctk.CTkLabel(
            parent, text="Options", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(14, 2), sticky="w")
        row += 1

        # Headless
        self._var_headless = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            parent, text="Headless (no browser window)", variable=self._var_headless
        ).grid(row=row, column=1, **pad)
        row += 1

        # Slow Mo
        ctk.CTkLabel(parent, text="Slow Mo (ms)").grid(row=row, column=0, **pad)
        spin_frame = ctk.CTkFrame(parent, fg_color="transparent")
        spin_frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        self._var_slowmo = ctk.StringVar(value="200")
        ctk.CTkEntry(spin_frame, width=80, textvariable=self._var_slowmo).pack(
            side="left"
        )
        ctk.CTkLabel(spin_frame, text="(50–500)").pack(side="left", padx=6)
        row += 1

        # --- buttons ----------------------------------------------------------------
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16, sticky="w", padx=10)
        ctk.CTkButton(
            btn_frame, text="Save Config", width=130, command=self._save_config
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btn_frame, text="Load Config", width=130, command=self._load_config
        ).pack(side="left")

    # -------------------------------------------------------------------
    # Info icon helpers
    # -------------------------------------------------------------------

    def _make_label_with_info(
        self, parent: ctk.CTkFrame, text: str, info_text: str
    ) -> ctk.CTkFrame:
        """Return a frame containing a label and a hoverable ⓘ info icon."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(frame, text=text).pack(side="left")

        icon = ctk.CTkLabel(
            frame,
            text=" ⓘ",
            text_color="#1565C0",
            cursor="hand2",
            font=ctk.CTkFont(size=11),
        )
        icon.pack(side="left", padx=(3, 0))
        icon.bind(
            "<Enter>", lambda e, w=icon, t=info_text: self._show_info_tooltip(w, t)
        )
        icon.bind("<Leave>", lambda _e: self._hide_info_tooltip())

        return frame

    def _show_info_tooltip(
        self, anchor_widget: ctk.CTkLabel, info_text: str
    ) -> None:
        """Show a borderless tooltip below *anchor_widget* on hover."""
        self._hide_info_tooltip()

        tip = ctk.CTkToplevel(self)
        self._info_tooltip = tip
        tip.overrideredirect(True)
        tip.configure(fg_color=("gray90", "gray25"))

        ctk.CTkLabel(
            tip,
            text=info_text,
            wraplength=320,
            justify="left",
            fg_color="transparent",
        ).pack(padx=12, pady=8)

        self.update_idletasks()
        x = anchor_widget.winfo_rootx()
        y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height() + 4
        tip.geometry(f"+{x}+{y}")

        tip.bind("<Leave>", lambda _e: self._hide_info_tooltip())

    def _hide_info_tooltip(self) -> None:
        if hasattr(self, "_info_tooltip") and self._info_tooltip is not None:
            try:
                self._info_tooltip.destroy()
            except Exception:
                pass
            self._info_tooltip = None

    # -------------------------------------------------------------------
    # Config helpers
    # -------------------------------------------------------------------

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

    def _apply_config(self, cfg: LogbookConfig) -> None:
        self._ent_username.delete(0, "end")
        self._ent_username.insert(0, cfg.username)
        self._ent_password.delete(0, "end")
        self._ent_password.insert(0, cfg.password)
        self._ent_dosen.delete(0, "end")
        self._ent_dosen.insert(0, cfg.dosen)
        self._ent_row.delete(0, "end")
        self._ent_row.insert(0, cfg.row_number)
        self._ent_semester.delete(0, "end")
        self._ent_semester.insert(0, cfg.semester)
        self._ent_csv.delete(0, "end")
        self._ent_csv.insert(0, cfg.csv_path)
        self._var_headless.set(cfg.headless)
        self._var_slowmo.set(str(cfg.slow_mo))

    def _browse_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self._ent_csv.delete(0, "end")
            self._ent_csv.insert(0, path)

    def _save_config(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self._gather_config().save_to_file(path)
            self._log(f"Config saved to {path}")
        except Exception as e:
            self._log(f"Failed to save config: {e}")

    def _load_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Load configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            cfg = LogbookConfig.load_from_file(path)
            self._apply_config(cfg)
            self._log(f"Config loaded from {path} (password cleared)")
        except Exception as e:
            self._log(f"Failed to load config: {e}")

    # =======================================================================
    # Tab 2 — Logbook Data (editable table)
    # =======================================================================

    def _build_data_tab(self) -> None:
        parent = self._tab_data

        # -- toolbar ----------------------------------------------------------------
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(10, 4))

        ctk.CTkButton(toolbar, text="Load CSV", width=100, command=self._load_csv).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(toolbar, text="Add Row", width=90, command=self._add_row).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(
            toolbar, text="Delete Last", width=100, command=self._delete_last_row
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(toolbar, text="Save CSV", width=90, command=self._save_csv).pack(
            side="left"
        )

        # -- header row -------------------------------------------------------------
        header_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", padx=10, pady=(6, 0))
        col_widths = [10, 7, 7, 14, 8, 5, 10, 8]  # relative widths
        for idx, col_name in enumerate(CSV_COLUMNS):
            lbl = ctk.CTkLabel(
                header_frame,
                text=col_name.capitalize(),
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=4)
            header_frame.grid_columnconfigure(idx, weight=col_widths[idx])

        # -- scrollable table body --------------------------------------------------
        self._table_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self._table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._table_frame.grid_columnconfigure(list(range(8)), weight=1)

        self._table_rows.clear()

    # -------------------------------------------------------------------
    # Table row management
    # -------------------------------------------------------------------

    def _make_row_widgets(
        self, parent_frame: ctk.CTkFrame, row_idx: int
    ) -> dict[str, Any]:
        """Create one row of entry/combo widgets; return ref dict."""
        widgets: dict[str, Any] = {}
        col = 0

        # tanggal
        w = ctk.CTkEntry(parent_frame, width=90)
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["tanggal"] = w
        col += 1

        # mulai
        w = ctk.CTkEntry(parent_frame, width=65)
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["mulai"] = w
        col += 1

        # selesai
        w = ctk.CTkEntry(parent_frame, width=65)
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["selesai"] = w
        col += 1

        # keterangan
        w = ctk.CTkEntry(parent_frame)
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["keterangan"] = w
        col += 1

        # file + browse button
        file_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        file_frame.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        file_frame.grid_columnconfigure(0, weight=1)
        w_file = ctk.CTkEntry(file_frame)
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
        w = ctk.CTkEntry(parent_frame)
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["lokasi"] = w
        col += 1

        # berita
        w = ctk.CTkComboBox(parent_frame, values=BERITA_VALUES, width=105)
        w.set("kegiatan")
        w.grid(row=row_idx, column=col, sticky="ew", padx=2, pady=2)
        widgets["berita"] = w

        return widgets

    def _browse_file_cell(self, entry_widget: ctk.CTkEntry) -> None:
        path = filedialog.askopenfilename(title="Select file")
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _clear_table(self) -> None:
        for row_data in self._table_rows:
            for w in row_data.values():
                if isinstance(w, ctk.CTkEntry):
                    w.destroy()
                elif isinstance(w, ctk.CTkComboBox):
                    w.destroy()
                elif isinstance(w, ctk.CTkFrame):
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
        """Pad to at least 3 visible rows."""
        while len(self._table_rows) < 3:
            self._add_row()

    def _add_row(self) -> None:
        idx = len(self._table_rows)
        row_data = self._make_row_widgets(self._table_frame, idx)
        # defaults
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
            if isinstance(w, ctk.CTkEntry):
                w.destroy()
            elif isinstance(w, ctk.CTkComboBox):
                w.destroy()
            elif isinstance(w, ctk.CTkFrame):
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

    # =======================================================================
    # Tab 3 — Run
    # =======================================================================

    def _build_run_tab(self) -> None:
        parent = self._tab_run
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # -- control bar -----------------------------------------------------------
        ctrl = ctk.CTkFrame(parent, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        ctrl.grid_columnconfigure(1, weight=1)

        self._btn_run = ctk.CTkButton(
            ctrl,
            text="▶  Start",
            width=130,
            height=42,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._toggle_run,
        )
        self._btn_run.grid(row=0, column=0, padx=(0, 12))

        self._lbl_status = ctk.CTkLabel(
            ctrl,
            text="Ready",
            font=ctk.CTkFont(size=14),
        )
        self._lbl_status.grid(row=0, column=1, sticky="w")

        # -- progress bar ----------------------------------------------------------
        self._progress = ctk.CTkProgressBar(parent, height=12)
        self._progress.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self._progress.set(0)

        # -- log output -------------------------------------------------------------
        self._log_box = ctk.CTkTextbox(parent, wrap="word", state="disabled")
        self._log_box.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # =======================================================================
    # Run orchestration
    # =======================================================================

    def _toggle_run(self) -> None:
        if self._automator is not None and self._automator.is_running:
            # Stop
            self._automator.stop()
            self._btn_run.configure(text="⏹  Stopping...", state="disabled")
            return

        # Start
        cfg = self._gather_config()
        if not cfg.username or not cfg.password:
            self._log("⚠ Username and password are required.")
            return

        self._automator = LogbookAutomator(
            config=cfg,
            progress_callback=self._on_progress,
            log_callback=self._on_log,
        )

        # UI state
        self._set_running(True)
        self._lbl_status.configure(text="Running...", text_color="#f9a825")
        self._progress.set(0)
        self._clear_log()
        self._log(f"Starting automation with {cfg.csv_path}...")

        # Disable config & data tabs
        self._tabview.configure(state="disabled")

        # Thread
        self._thread = threading.Thread(target=self._run_worker, daemon=True)
        self._thread.start()

    def _set_running(self, running: bool) -> None:
        if running:
            self._btn_run.configure(
                text="⏹  Stop", fg_color="#c62828", hover_color="#8e0000"
            )
        else:
            self._btn_run.configure(
                text="▶  Start",
                fg_color="#2e7d32",
                hover_color="#1b5e20",
                state="normal",
            )

    def _run_worker(self) -> None:
        assert self._automator is not None
        try:
            success = self._automator.run()
            self._queue.put({"type": "done", "success": success})
        except Exception as e:
            self._queue.put({"type": "done", "success": False})
            self._queue.put({"type": "log", "message": f"❌ Fatal error: {e}"})

    def _on_progress(self, current: int, total: int, message: str) -> None:
        self._queue.put(
            {"type": "progress", "current": current, "total": total, "message": message}
        )

    def _on_log(self, message: str) -> None:
        self._queue.put({"type": "log", "message": message})

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self._queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "progress":
                    if msg["total"] > 0:
                        self._progress.set(msg["current"] / msg["total"])
                    self._append_log(f"[{_now_stamp()}] {msg['message']}")

                elif msg_type == "log":
                    self._append_log(f"[{_now_stamp()}] {msg['message']}")

                elif msg_type == "done":
                    success = msg.get("success", False)
                    self._on_done(success)

        except queue.Empty:
            pass
        finally:
            self.after(100, self._poll_queue)

    def _on_done(self, success: bool) -> None:
        self._set_running(False)
        self._tabview.configure(state="normal")
        if success:
            self._progress.set(1.0)
            self._lbl_status.configure(text="Completed ✓", text_color="#4caf50")
        else:
            self._lbl_status.configure(text="Failed ✗", text_color="#c62828")
        self._automator = None
        self._thread = None

    # =======================================================================
    # Log helpers
    # =======================================================================

    def _log(self, message: str) -> None:
        self._append_log(f"[{_now_stamp()}] {message}")

    def _append_log(self, text: str) -> None:
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_log(self) -> None:
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    # =======================================================================
    # Close / cleanup
    # =======================================================================

    def _on_close(self) -> None:
        if self._automator is not None and self._automator.is_running:
            self._automator.stop()
            # Give the worker a moment to finish
            time.sleep(0.5)
        self.destroy()


# ===================================================================
# Entry point
# ===================================================================


def main() -> None:
    app = LogbookApp()
    app.mainloop()


if __name__ == "__main__":
    main()
