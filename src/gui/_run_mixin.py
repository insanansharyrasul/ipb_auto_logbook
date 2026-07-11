"""Run tab — start/stop button, progress bar, log output, runner thread."""

from __future__ import annotations

import threading

import customtkinter as ctk

from src.automator import LogbookAutomator


class RunTabMixin:
    """Mixin that builds the Run tab and its orchestration logic."""

    # ------------------------------------------------------------------
    # Tab builder
    # ------------------------------------------------------------------

    def _build_run_tab(self) -> None:
        parent = self._tab_run
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # -- control bar ---------------------------------------------------
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

        self._lbl_status = ctk.CTkLabel(ctrl, text="Ready", font=ctk.CTkFont(size=14))
        self._lbl_status.grid(row=0, column=1, sticky="w")

        # -- progress bar --------------------------------------------------
        self._progress = ctk.CTkProgressBar(parent, height=12)
        self._progress.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self._progress.set(0)

        # -- log output ----------------------------------------------------
        self._log_box = ctk.CTkTextbox(parent, wrap="word", state="disabled")
        self._log_box.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    # Run orchestration
    # ------------------------------------------------------------------

    def _toggle_run(self) -> None:
        if self._automator is not None and self._automator.is_running:
            self._automator.stop()
            self._btn_run.configure(text="⏹  Stopping...", state="disabled")
            return

        cfg = self._gather_config()
        if not cfg.username or not cfg.password:
            self._log("⚠ Username and password are required.")
            return

        self._automator = LogbookAutomator(
            config=cfg,
            progress_callback=self._on_progress,
            log_callback=self._on_log,
        )

        self._set_running(True)
        self._lbl_status.configure(text="Running...", text_color="#f9a825")
        self._progress.set(0)
        self._clear_log()
        self._log(f"Starting automation with {cfg.csv_path}...")

        self._tabview.configure(state="disabled")

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
            {
                "type": "progress",
                "current": current,
                "total": total,
                "message": message,
            }
        )

    def _on_log(self, message: str) -> None:
        self._queue.put({"type": "log", "message": message})
