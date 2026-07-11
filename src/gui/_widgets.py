"""Reusable customtkinter widgets — info-label-with-tooltip mixin."""

from __future__ import annotations

import customtkinter as ctk


class InfoWidgetMixin:
    """Mixin providing hover-tooltip info labels."""

    def _make_label_with_info(
        self, parent: ctk.CTkFrame, text: str, info_text: str
    ) -> ctk.CTkFrame:
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
            "<Enter>",
            lambda e, w=icon, t=info_text: self._show_info_tooltip(w, t),
        )
        icon.bind("<Leave>", lambda _e: self._hide_info_tooltip())

        return frame

    def _show_info_tooltip(self, anchor_widget: ctk.CTkLabel, info_text: str) -> None:
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
