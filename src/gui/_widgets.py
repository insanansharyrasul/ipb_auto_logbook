"""Reusable widgets — info-label with a native hover tooltip."""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class InfoWidgetMixin:
    """Mixin providing a "label + ⓘ" widget with a native hover tooltip."""

    def _make_label_with_info(self, text: str, info_text: str) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)

        lay.addWidget(QLabel(text))

        icon = QLabel(" ⓘ")
        icon.setStyleSheet("color: #1565C0;")
        icon.setToolTip(info_text)  # Qt handles show/hide/positioning natively
        lay.addWidget(icon)
        lay.addStretch(1)

        return w
