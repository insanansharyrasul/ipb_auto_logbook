# PyInstaller spec — builds the Windows GUI as a onedir bundle.
#
#   pyinstaller ipb_auto_logbook.spec
#
# Chromium must be installed INTO the playwright package first, so it gets
# bundled by collect_all('playwright'):
#
#   PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium
#
# See .github/workflows/build-windows.yml for the full recipe.

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pkg in ("playwright"):
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
    runtime_hooks=["pyi_rth_playwright.py"],
    excludes=[],
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
