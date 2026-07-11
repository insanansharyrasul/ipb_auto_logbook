"""IPB Auto Logbook — Desktop GUI (CustomTkinter).

Launch with:  python gui_app.py
"""

from __future__ import annotations

import queue
import sys
import threading
import time
from datetime import datetime
from typing import Any, Optional

try:
    import customtkinter as ctk
except ImportError:
    print(
        "customtkinter is not installed.\n"
        "Install it with:  pip install customtkinter"
    )
    sys.exit(1)

from src.automator import LogbookAutomator
from src.gui._widgets import InfoWidgetMixin
from src.gui._config_mixin import ConfigTabMixin
from src.gui._data_mixin import DataTabMixin
from src.gui._run_mixin import RunTabMixin
from src.gui._about_mixin import AboutTabMixin
from src.gui._constants import APP_VERSION

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ===================================================================
# Main Application
# ===================================================================


class LogbookApp(
    InfoWidgetMixin,
    ConfigTabMixin,
    DataTabMixin,
    RunTabMixin,
    AboutTabMixin,
    ctk.CTk,
):
    """Root application window — composes tabs via mixins."""

    def __init__(self) -> None:
        super().__init__()

        # -- window ----------------------------------------------------------
        self.title(f"IPB Auto Logbook v{APP_VERSION}")
        self.geometry("900x700")
        self.minsize(800, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # -- state -----------------------------------------------------------
        self._automator: Optional[LogbookAutomator] = None
        self._thread: Optional[threading.Thread] = None  # type: ignore[assignment]
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._table_rows: list[dict[str, Any]] = []

        # -- build UI --------------------------------------------------------
        self._build_tabview()
        self._build_config_tab()
        self._build_data_tab()
        self._build_run_tab()
        self._build_about_tab()

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
        self._tab_about = self._tabview.add("About")

        self._tabview.set("Configuration")

    # =======================================================================
    # Queue polling (processes messages from worker thread)
    # =======================================================================

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
