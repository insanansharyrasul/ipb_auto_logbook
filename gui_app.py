"""IPB Auto Logbook — Desktop GUI (PyQt6).

Launch with:  python gui_app.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
except ImportError:
    print("PyQt6 is not installed.\nInstall it with:  pip install PyQt6")
    sys.exit(1)

from src.gui._about_mixin import AboutTabMixin
from src.gui._config_mixin import ConfigTabMixin
from src.gui._constants import APP_VERSION
from src.gui._data_mixin import DataTabMixin
from src.gui._run_mixin import RunTabMixin, _RunWorker
from src.gui._widgets import InfoWidgetMixin


def _now_stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


class LogbookApp(
    InfoWidgetMixin,
    ConfigTabMixin,
    DataTabMixin,
    RunTabMixin,
    AboutTabMixin,
    QMainWindow,
):
    """Root application window — composes tabs via mixins."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(f"IPB Auto Logbook v{APP_VERSION}")
        self.resize(900, 700)
        self.setMinimumSize(800, 600)

        # -- state -----------------------------------------------------------
        self._worker: Optional[_RunWorker] = None
        self._table_rows: list[dict] = []

        # -- build UI --------------------------------------------------------
        self._tabview = QTabWidget()
        self.setCentralWidget(self._tabview)

        self._build_config_tab()
        self._build_data_tab()
        self._build_run_tab()
        self._build_about_tab()

        self._tabview.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _log(self, message: str) -> None:
        self._append_log(f"[{_now_stamp()}] {message}")

    def _append_log(self, text: str) -> None:
        self._log_box.append(text)  # QTextEdit.append auto-scrolls to the bottom

    def _clear_log(self) -> None:
        self._log_box.clear()

    # ------------------------------------------------------------------
    # Close / cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.automator.stop()
            self._worker.wait(3000)  # let the current entry finish, then close
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    window = LogbookApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
