"""About tab — version, maintainers, license."""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from src.gui._constants import APP_MAINTAINERS, APP_VERSION


class AboutTabMixin:
    """Mixin that builds the About tab."""

    def _build_about_tab(self) -> None:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(20, 24, 20, 20)
        root.setSpacing(4)

        title = QLabel(f"IPB Auto Logbook v{APP_VERSION}")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        root.addWidget(title)

        root.addWidget(
            QLabel("Automated logbook filler for IPB University Student Portal")
        )

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet("color: gray;")
        root.addSpacing(8)
        root.addWidget(rule)
        root.addSpacing(8)

        entries = (
            ("Contributors", "\n".join(APP_MAINTAINERS)),
            ("Original repository", "github.com/insanansharyrasul/ipb_auto_logbook"),
            ("License", "GNU General Public License v3.0"),
        )
        for heading, value in entries:
            h = QLabel(heading)
            h.setStyleSheet("font-weight: bold;")
            root.addWidget(h)
            v = QLabel(value)
            v.setStyleSheet("color: gray;")
            root.addWidget(v)
            root.addSpacing(8)

        root.addStretch(1)
        self._tabview.addTab(page, "About")
