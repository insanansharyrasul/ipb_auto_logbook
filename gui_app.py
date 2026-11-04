"""IPB Auto Logbook Desktop GUI (PyQt6 + QtQuick/QML).

Launch with:  python gui_app.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

from PyQt6.QtCore import QUrl
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PyQt6.QtWidgets import QApplication

from src.gui.controller import AppController

APP_VERSION = "1.0.0"  # QML reads it as Qt.application.version

# PyInstaller points __file__ into the bundle, where the spec copies src/gui/qml.
MAIN_QML = Path(__file__).resolve().parent / "src" / "gui" / "qml" / "Main.qml"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("IPB Auto Logbook")
    app.setApplicationVersion(APP_VERSION)

    controller = AppController()
    qmlRegisterSingletonInstance("App", 1, 0, "Controller", controller)
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile(str(MAIN_QML)))

    if not engine.rootObjects():
        sys.exit(1)

    app.aboutToQuit.connect(controller.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
