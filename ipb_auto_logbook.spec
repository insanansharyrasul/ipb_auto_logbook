# PyInstaller spec — builds the Windows GUI as a onedir bundle.
#
#   pyinstaller ipb_auto_logbook.spec
#
# No Chromium is bundled: the app drives the user's system Edge/Chrome
# (see Automator._launch_browser). Only Playwright's own driver is collected.

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pkg in ("playwright",):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["gui_app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["pandas", "numpy", "tkinter"],
    noarchive=False,
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
