# PyInstaller runtime hook: run before the app's own code.
# Chromium is collected into the bundled `playwright` package, so tell
# Playwright to look for it there (PLAYWRIGHT_BROWSERS_PATH=0 == "beside the
# package") instead of the user's per-machine cache.
import os

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
