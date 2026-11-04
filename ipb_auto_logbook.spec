# PyInstaller spec: builds the Windows GUI as a onedir bundle.
#
# Run: pyinstaller ipb_auto_logbook.spec
#
# No Chromium is bundled: the app drives the user's system Edge/Chrome
# (see LogbookAutomator._launch_browser). Only Playwright's own driver is collected.

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("playwright")
datas += [("src/gui/qml", "src/gui/qml")]
hiddenimports += ["PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.QtSvg"]

a = Analysis(
    ["gui_app.py"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["pandas", "numpy", "tkinter"],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IPB-Auto-Logbook",
    console=False,  # GUI app; logs show in the window
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="IPB-Auto-Logbook",
)
