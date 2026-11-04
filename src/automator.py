"""Core logbook automation logic for IPB Student Portal."""

import csv
import json
import sys
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Optional

from playwright.sync_api import sync_playwright

CSV_COLUMNS = ["tanggal", "mulai", "selesai", "keterangan", "file", "tipe", "lokasi", "berita"]
TIPE_OPTIONS = ("offline", "online", "hybrid")  # portal labels are the capitalized form
BERITA_OPTIONS = {
    "kegiatan": "Berita Acara Kegiatan",
    "ujian": "Berita Acara Ujian",
    "bimbingan": "Berita Acara Pembimbingan (Konsultasi/Mentoring/Coaching)",
}


def _base_dir() -> Path:
    """Directory that holds user data (data.csv, files/).

    Frozen exe: the folder the .exe sits in, so users edit data next to it.
    Dev: the project root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def resolve_to_absolute_path(file_path: str) -> str:
    """Resolve a path relative to the user-data dir to an absolute path."""
    return str((_base_dir() / file_path).resolve())


def clean_string(string: str) -> str:
    """Normalize a string: lowercase and strip whitespace."""
    return string.lower().replace(" ", "")


@dataclass
class LogbookConfig:
    """Configuration for a logbook automation run."""

    username: str = ""
    password: str = ""
    dosen: str = ""
    row_number: str = ""
    semester: str = ""
    csv_path: str = "data.csv"
    headless: bool = False
    slow_mo: int = 200

    def save_to_file(self, path: str) -> None:
        """Save config to a JSON file (excluding password)."""
        data = asdict(self)
        del data["password"]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> "LogbookConfig":
        """Load config from a JSON file. Password must be provided separately."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls(password="", **data)


class LogbookAutomator:
    """Orchestrates Playwright-based logbook automation.

    Runs in a background thread; communicates progress via callbacks.
    """

    PORTAL_LOGIN = "https://studentportal.ipb.ac.id/Account/Login"
    PORTAL_HOME = "https://studentportal.ipb.ac.id/"
    PORTAL_AKTIVITAS = "https://studentportal.ipb.ac.id/Kegiatan/AktivitasKampusMerdeka"

    def __init__(
        self,
        config: LogbookConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self._progress_cb = progress_callback or (lambda *_: None)
        self._log_cb = log_callback or (lambda _: None)
        self._stop_flag = threading.Event()

    def run(self) -> bool:
        """Execute the automation. Returns True on success, False on failure/stop."""
        self._stop_flag.clear()

        try:
            with open(
                resolve_to_absolute_path(self.config.csv_path),
                newline="",
                encoding="utf-8",
            ) as f:
                rows = [{c: r.get(c) or "" for c in CSV_COLUMNS} for r in csv.DictReader(f)]
        except Exception as e:
            self._log_cb(f"❌ Failed to read CSV: {e}")
            return False
        total = len(rows)

        # Leaving the sync_playwright() block closes the browser on every exit path.
        try:
            with sync_playwright() as p:
                page = self._launch_browser(p).new_page()
                if not (self._login(page) and self._navigate_to_form(page)):
                    return False

                for i, row in enumerate(rows):
                    if self._stop_flag.is_set():
                        self._log_cb("Stopped by user.")
                        return False

                    self._progress_cb(i, total, f"Filling entry {i + 1}/{total}...")
                    self._log_cb(f"Entry {i + 1}/{total}: {row['keterangan']}")

                    if not self._fill_entry(page, row):
                        self._log_cb(f"Skipped entry {i + 1} due to error")
                        continue

                    page.get_by_role("button", name="Simpan").click()
                    time.sleep(1)

                    # Click "Tambah" for next entry
                    if i < total - 1:
                        try:
                            page.get_by_text("Tambah").first.click()
                        except Exception:
                            self._log_cb("⚠ Could not click 'Tambah' for next entry")

                self._progress_cb(total, total, "Done!")
                self._log_cb("All entries submitted.")

        except Exception as e:
            self._log_cb(f"❌ Unexpected error: {e}")
            return False

        return True

    def stop(self) -> None:
        """Request graceful stop at the next entry boundary."""
        self._log_cb("⏸ Stop requested... waiting for current entry to finish.")
        self._stop_flag.set()

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------

    def _launch_browser(self, p):
        """Use the system Edge/Chrome instead of a bundled Chromium."""
        for channel in ("msedge", "chrome"):
            try:
                return p.chromium.launch(
                    channel=channel,
                    headless=self.config.headless,
                    slow_mo=self.config.slow_mo,
                )
            except Exception:
                continue
        raise RuntimeError(
            "No Microsoft Edge or Google Chrome found. Please install one of them."
        )

    def _login(self, page) -> bool:
        self._log_cb("Logging in...")
        try:
            page.goto(self.PORTAL_LOGIN)
            page.get_by_placeholder("Username").fill(self.config.username)
            page.get_by_placeholder("Password").fill(self.config.password)
            page.get_by_role("button", name="Masuk").click()
            page.wait_for_url(self.PORTAL_HOME, timeout=15000)
            self._log_cb("✅ Login successful")
            return True
        except Exception:
            error = page.get_by_text("Login gagal. Username atau password Anda salah.")
            try:
                error.wait_for(state="visible", timeout=2000)
                self._log_cb("❌ Login failed: Username atau password Anda salah.")
            except Exception:
                self._log_cb("❌ Login failed: Could not reach portal.")
            return False

    def _navigate_to_form(self, page) -> bool:
        self._log_cb("Navigating to logbook form...")
        try:
            page.goto(self.PORTAL_AKTIVITAS)
            row_matcher = f"{self.config.row_number} {self.config.semester}"
            page.get_by_role("row", name=row_matcher).get_by_role("link").nth(2).click()
            page.get_by_text("Tambah").click()
            self._log_cb("Form opened")
            return True
        except Exception as e:
            self._log_cb(f"❌ Navigation failed: {e}")
            return False

    def _fill_entry(self, page, row: dict[str, str]) -> bool:
        """Fill one form entry from a CSV row (keys: CSV_COLUMNS)."""
        try:
            # Tanggal
            page.get_by_placeholder("Tanggal").click()
            page.get_by_placeholder("Tanggal").type(clean_string(row["tanggal"]))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Waktu Selesai
            page.get_by_placeholder("Waktu Selesai").click()
            for _ in range(5):
                page.keyboard.press("Backspace")
            page.get_by_placeholder("Waktu Selesai").type(clean_string(row["selesai"]))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Waktu Mulai
            page.get_by_placeholder("Waktu Mulai").click()
            for _ in range(5):
                page.keyboard.press("Backspace")
            page.get_by_placeholder("Waktu Mulai").type(clean_string(row["mulai"]))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Berita Acara
            page.get_by_role("textbox", name="-- Pilih --").click()
            berita = BERITA_OPTIONS.get(clean_string(row["berita"]))
            if not berita:
                self._log_cb(f"Unknown berita type: {row['berita']}")
                return False
            page.get_by_role("option", name=berita).click()

            # Dosen Penggerak
            page.get_by_label(self.config.dosen).check()

            # Tipe
            tipe = clean_string(row["tipe"])
            if tipe not in TIPE_OPTIONS:
                self._log_cb(f"Unknown tipe: {row['tipe']}")
                return False
            page.get_by_label(tipe.capitalize()).check()

            # Lokasi
            page.get_by_placeholder("Lokasi").fill(row["lokasi"])

            # Topik
            page.get_by_placeholder("Topik").fill(row["keterangan"])

            # File
            file_path = resolve_to_absolute_path(row["file"])
            if not Path(file_path).exists():
                self._log_cb(f"File not found: {file_path}")
                return False
            page.locator("#File").set_input_files(file_path)

            return True

        except Exception as e:
            self._log_cb(f"❌ Error filling entry: {e}")
            return False


if __name__ == "__main__":
    # Self-check: config save/load round-trip (used by the GUI Save/Load buttons).
    import tempfile

    cfg = LogbookConfig(
        username="alice",
        password="secret",
        dosen="Jeffrey Einstein, S.Komp., Ph.D.",
        row_number="1",
        semester="2026/2027 Semester Genap",
        csv_path="data.csv",
        headless=True,
        slow_mo=123,
    )
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        cfg.save_to_file(f.name)
        loaded = LogbookConfig.load_from_file(f.name)

    assert loaded == LogbookConfig(**{**asdict(cfg), "password": ""})
    assert loaded.password == "", "password must never be persisted"

    # Dev-mode base dir resolves under the project root, not sys.executable.
    assert resolve_to_absolute_path("data.csv").endswith("data.csv")
    assert (
        Path(resolve_to_absolute_path("data.csv")).parent
        == Path(__file__).parent.parent
    )

    print("self-check OK: config round-trip preserved (password excluded)")
