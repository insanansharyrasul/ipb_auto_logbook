"""Run tab — start/stop button, progress bar, log output, runner thread."""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.automator import LogbookAutomator, LogbookConfig

_BTN_GREEN = "QPushButton { background: #2e7d32; color: white; font-weight: bold; }"
_BTN_RED = "QPushButton { background: #c62828; color: white; font-weight: bold; }"


class _RunWorker(QThread):
    """Runs the automator off the UI thread, relaying its callbacks as signals."""

    progress = pyqtSignal(int, int, str)
    log = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, config: LogbookConfig) -> None:
        super().__init__()
        # Callbacks fire on this thread; Qt marshals the signals to the UI thread.
        self.automator = LogbookAutomator(
            config=config,
            progress_callback=self.progress.emit,
            log_callback=self.log.emit,
        )

    def run(self) -> None:
        try:
            self.done.emit(self.automator.run())
        except Exception as e:
            self.log.emit(f"❌ Fatal error: {e}")
            self.done.emit(False)


class RunTabMixin:
    """Mixin that builds the Run tab and its orchestration logic."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_run_tab(self) -> None:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(10, 10, 10, 10)

        # -- control bar ---------------------------------------------------
        ctrl = QHBoxLayout()
        self._btn_run = QPushButton("▶  Start")
        self._btn_run.setFixedSize(130, 42)
        self._btn_run.setStyleSheet(_BTN_GREEN)
        self._btn_run.clicked.connect(self._toggle_run)
        ctrl.addWidget(self._btn_run)

        self._lbl_status = QLabel("Ready")
        ctrl.addWidget(self._lbl_status)
        ctrl.addStretch(1)
        root.addLayout(ctrl)

        # -- progress bar --------------------------------------------------
        self._progress = QProgressBar()
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(12)
        self._progress.setRange(0, 1)
        self._progress.setValue(0)
        root.addWidget(self._progress)

        # -- log output ----------------------------------------------------
        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        root.addWidget(self._log_box, 1)

        self._tabview.addTab(page, "Run")

    # ------------------------------------------------------------------
    # Run orchestration
    # ------------------------------------------------------------------

    def _toggle_run(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.automator.stop()
            self._btn_run.setText("⏹  Stopping...")
            self._btn_run.setEnabled(False)
            return

        cfg = self._gather_config()
        if not cfg.username or not cfg.password:
            self._log("⚠ Username and password are required.")
            return

        self._worker = _RunWorker(cfg)
        self._worker.progress.connect(self._on_progress)
        self._worker.log.connect(self._on_log)
        self._worker.done.connect(self._on_done)

        self._set_running(True)
        self._lbl_status.setText("Running...")
        self._lbl_status.setStyleSheet("color: #f9a825;")
        self._progress.setRange(0, 1)
        self._progress.setValue(0)
        self._clear_log()
        self._log(f"Starting automation with {cfg.csv_path}...")
        self._set_tabs_locked(True)
        self._worker.start()

    def _set_running(self, running: bool) -> None:
        if running:
            self._btn_run.setText("⏹  Stop")
            self._btn_run.setStyleSheet(_BTN_RED)
        else:
            self._btn_run.setText("▶  Start")
            self._btn_run.setStyleSheet(_BTN_GREEN)
            self._btn_run.setEnabled(True)

    def _set_tabs_locked(self, locked: bool) -> None:
        """Prevent leaving the Run tab while a run is in progress."""
        for i in range(self._tabview.count()):
            if self._tabview.tabText(i) != "Run":
                self._tabview.setTabEnabled(i, not locked)

    # -- worker signal slots -------------------------------------------

    def _on_progress(self, current: int, total: int, message: str) -> None:
        if total > 0:
            self._progress.setMaximum(total)
            self._progress.setValue(current)
        self._log(message)

    def _on_log(self, message: str) -> None:
        self._log(message)

    def _on_done(self, success: bool) -> None:
        self._set_running(False)
        self._set_tabs_locked(False)
        if success:
            self._progress.setMaximum(1)
            self._progress.setValue(1)
            self._lbl_status.setText("Completed ✓")
            self._lbl_status.setStyleSheet("color: #4caf50;")
        else:
            self._lbl_status.setText("Failed ✗")
            self._lbl_status.setStyleSheet("color: #c62828;")
        self._worker = None
