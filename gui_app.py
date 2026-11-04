"""IPB Auto Logbook Desktop GUI (PyQt6 + QtQuick/QML).

Launch with:  python gui_app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

try:
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QFont, QFontDatabase
    from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("PyQt6 is not installed.\nInstall it with:  pip install PyQt6")
    sys.exit(1)

from src.gui._constants import APP_VERSION
from src.gui.controller import AppController


def _main_qml() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        return base / "src" / "gui" / "qml" / "Main.qml"
    return Path(__file__).resolve().parent / "src" / "gui" / "qml" / "Main.qml"


def _pick_font() -> QFont:
    families = set(QFontDatabase.families())
    for family in (
        "Inter",
        "Segoe UI Variable Text",
        "Segoe UI",
        "SF Pro Text",
        "Cantarell",
        "Ubuntu",
        "DejaVu Sans",
    ):
        if family in families:
            return QFont(family, 10)
    return QFont()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("IPB Auto Logbook")
    app.setApplicationVersion(APP_VERSION)
    app.setFont(_pick_font())

    controller = AppController()
    qmlRegisterSingletonInstance("App", 1, 0, "Controller", controller)
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile(str(_main_qml())))

    if not engine.rootObjects():
        sys.exit(1)

    app.aboutToQuit.connect(controller.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
