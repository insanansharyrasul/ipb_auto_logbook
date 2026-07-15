"""Core logbook automation logic for IPB Student Portal."""

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
from playwright.sync_api import sync_playwright


def resolve_to_absolute_path(file_path: str) -> str:
    """Resolve a path relative to the project root to an absolute path."""
    project_root = Path(__file__).parent.parent
    return str((project_root / file_path).resolve())


def clean_string(string: str) -> str:
    """Normalize a string: lowercase and strip whitespace."""
    return string.lower().replace(" ", "")


@dataclass
class LogbookRow:
    """A single logbook entry."""

    tanggal: str  # DD/MM/YYYY
    mulai: str  # HH:MM
    selesai: str  # HH:MM
    keterangan: str  # description / topic
    file: str  # relative path under files/
    tipe: str  # offline / online / hybrid
    lokasi: str  # location
    berita: str  # kegiatan / ujian / bimbingan


@dataclass
class LogbookConfig:
    """Configuration for a logbook automation run."""

    username: str
    password: str
    dosen: str
    row_number: str
    semester: str
    csv_path: str = "data.csv"
    headless: bool = False
    slow_mo: int = 200

    def save_to_file(self, path: str) -> None:
        """Save config to a JSON file (excluding password)."""
        import json

        data = {
            "username": self.username,
            "dosen": self.dosen,
            "row_number": self.row_number,
            "semester": self.semester,
            "csv_path": self.csv_path,
            "headless": self.headless,
            "slow_mo": self.slow_mo,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> "LogbookConfig":
        """Load config from a JSON file. Password must be provided separately."""
        import json

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
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> bool:
        """Execute the automation. Returns True on success, False on failure/stop."""
        self._stop_flag.clear()
        self._running = True

        try:
            df = pd.read_csv(resolve_to_absolute_path(self.config.csv_path))
            total = df.shape[0]
        except Exception as e:
            self._log_cb(f"❌ Failed to read CSV: {e}")
            self._running = False
            return False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.config.headless,
                    slow_mo=self.config.slow_mo,
                )
                page = browser.new_page()

                if not self._login(page):
                    browser.close()
                    self._running = False
                    return False

                if not self._navigate_to_form(page):
                    browser.close()
                    self._running = False
                    return False

                for i in range(total):
                    if self._stop_flag.is_set():
                        self._log_cb("Stopped by user.")
                        browser.close()
                        self._running = False
                        return False

                    row = LogbookRow(
                        tanggal=str(df["tanggal"][i]),
                        mulai=str(df["mulai"][i]),
                        selesai=str(df["selesai"][i]),
                        keterangan=str(df["keterangan"][i]),
                        file=str(df["file"][i]),
                        tipe=str(df["tipe"][i]),
                        lokasi=str(df["lokasi"][i]),
                        berita=str(df["berita"][i]),
                    )

                    self._progress_cb(i, total, f"Filling entry {i + 1}/{total}...")
                    self._log_cb(f"Entry {i + 1}/{total}: {row.keterangan}")

                    if not self._fill_entry(page, row):
                        self._log_cb(f"Skipped entry {i + 1} due to error")
                        continue

                    self._click_save(page)
                    time.sleep(1)

                    # Click "Tambah" for next entry
                    if i < total - 1:
                        try:
                            page.get_by_text("Tambah").first.click()
                        except Exception:
                            self._log_cb("⚠ Could not click 'Tambah' for next entry")

                self._progress_cb(total, total, "Done!")
                self._log_cb("All entries submitted.")
                browser.close()

        except Exception as e:
            self._log_cb(f"❌ Unexpected error: {e}")
            self._running = False
            return False

        self._running = False
        return True

    def stop(self) -> None:
        """Request graceful stop at the next entry boundary."""
        self._log_cb("⏸ Stop requested... waiting for current entry to finish.")
        self._stop_flag.set()

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------

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

    def _fill_entry(self, page, row: LogbookRow) -> bool:
        try:
            # Tanggal
            page.get_by_placeholder("Tanggal").click()
            page.get_by_placeholder("Tanggal").type(clean_string(row.tanggal))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Waktu Selesai
            page.get_by_placeholder("Waktu Selesai").click()
            for _ in range(5):
                page.keyboard.press("Backspace")
            page.get_by_placeholder("Waktu Selesai").type(clean_string(row.selesai))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Waktu Mulai
            page.get_by_placeholder("Waktu Mulai").click()
            for _ in range(5):
                page.keyboard.press("Backspace")
            page.get_by_placeholder("Waktu Mulai").type(clean_string(row.mulai))
            page.get_by_placeholder("Tanggal").press("Escape")

            # Berita Acara
            page.get_by_role("textbox", name="-- Pilih --").click()
            berita_clean = clean_string(row.berita)
            if berita_clean == "kegiatan":
                page.get_by_role("option", name="Berita Acara Kegiatan").click()
            elif berita_clean == "ujian":
                page.get_by_role("option", name="Berita Acara Ujian").click()
            elif berita_clean == "bimbingan":
                page.get_by_role(
                    "option",
                    name="Berita Acara Pembimbingan (Konsultasi/Mentoring/Coaching)",
                ).click()
            else:
                self._log_cb(f"Unknown berita type: {row.berita}")
                return False

            # Dosen Penggerak
            page.get_by_label(self.config.dosen).check()

            # Tipe
            tipe_clean = clean_string(row.tipe)
            if tipe_clean == "offline":
                page.get_by_label("Offline").check()
            elif tipe_clean == "online":
                page.get_by_label("Online").check()
            elif tipe_clean == "hybrid":
                page.get_by_label("Hybrid").check()
            else:
                self._log_cb(f"Unknown tipe: {row.tipe}")
                return False

            # Lokasi
            page.get_by_placeholder("Lokasi").fill(row.lokasi)

            # Topik
            page.get_by_placeholder("Topik").fill(row.keterangan)

            # File
            file_path = resolve_to_absolute_path(row.file)
            if not Path(file_path).exists():
                self._log_cb(f"File not found: {file_path}")
                return False
            page.locator("#File").set_input_files(file_path)

            return True

        except Exception as e:
            self._log_cb(f"❌ Error filling entry: {e}")
            return False

    def _click_save(self, page) -> None:
        page.get_by_role("button", name="Simpan").click()


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

    assert loaded.username == cfg.username
    assert loaded.dosen == cfg.dosen
    assert loaded.row_number == cfg.row_number
    assert loaded.semester == cfg.semester
    assert loaded.csv_path == cfg.csv_path
    assert loaded.headless == cfg.headless
    assert loaded.slow_mo == cfg.slow_mo
    assert loaded.password == "", "password must never be persisted"
    print("self-check OK: config round-trip preserved (password excluded)")
