"""About tab — version, maintainers, license."""

from __future__ import annotations

import customtkinter as ctk

from src.gui._constants import APP_MAINTAINERS, APP_VERSION


class AboutTabMixin:
    """Mixin that builds the About tab."""

    def _build_about_tab(self) -> None:
        parent = self._tab_about
        parent.grid_columnconfigure(0, weight=1)

        PX, PY = 20, 8

        ctk.CTkLabel(
            parent,
            text=f"IPB Auto Logbook v{APP_VERSION}",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=PX, pady=(24, 2), sticky="w")

        ctk.CTkLabel(
            parent,
            text="Automated logbook filler for IPB University Student Portal",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, padx=PX, pady=(0, PY), sticky="w")

        ctk.CTkFrame(parent, height=1, fg_color=("gray70", "gray40")).grid(
            row=3, column=0, sticky="ew", padx=PX, pady=(0, 12)
        )

        entries = (
            ("Contributors", "\n".join(APP_MAINTAINERS)),
            (
                "Original repository",
                "github.com/insanansharyrasul/ipb_auto_logbook",
            ),
            ("License", "GNU General Public License v3.0"),
        )
        for i, (title, value) in enumerate(entries):
            base = 4 + i * 2
            ctk.CTkLabel(
                parent,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=base, column=0, padx=PX, pady=(6, 0), sticky="w")
            ctk.CTkLabel(
                parent,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60"),
            ).grid(row=base + 1, column=0, padx=PX, pady=(0, 12), sticky="w")
