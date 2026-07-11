"""IPB AUTO LOGBOOK"""

from getpass import getpass
from pathlib import Path

import time
from playwright.sync_api import sync_playwright
import pandas as pd


def resolve_to_absolute_path(file_path):
    """Resolves a file path to an absolute path."""
    return str((Path(__file__).parent / file_path).resolve())


def clean_string(string):
    """Cleans a string by converting it to lowercase and removing spaces."""
    string = string.lower().replace(" ", "")
    return string


# Input Data
source = "data.csv"    # Jika nama csv-nya bukan data.csv, silakan ganti
df = pd.read_csv(resolve_to_absolute_path(source))

USERNAME = input("Username: ")
PASSWORD = getpass("Password: ")

DOSEN = "nama_dosen"  # Example: "Jeffrey Einstein, S.Komp., Ph.D."
ROW_NUMBER = "row_number"  # Example: "1" for the first row, or "2" for the second row
SEMESTER = "YYYY/YYYY Semester Ganjil/Genap"  # Example: "2023/2024 Semester Genap"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page()

    page.goto("https://studentportal.ipb.ac.id/Account/Login")

    # Login
    page.get_by_placeholder("Username").fill(USERNAME)
    page.get_by_placeholder("Password").fill(PASSWORD)
    page.get_by_role("button", name="Masuk").click()

    page.wait_for_url("https://studentportal.ipb.ac.id/")
    page.goto("https://studentportal.ipb.ac.id/Kegiatan/AktivitasKampusMerdeka")

    page.get_by_role(
        "row",
        name=f"{ROW_NUMBER} {SEMESTER}",
    ).get_by_role("link").nth(2).click()

    page.get_by_text("Tambah").click()

    # Logbook
    for i in range(df.shape[0]):
        # Jenis Kegiatan
        page.locator("#select2-JenisLogbookKegiatanKampusMerdekaId-container").click()

        if clean_string(df["jenis_kegiatan"][i]) == "kegiatan":
            page.get_by_role("option", name="Berita Acara Kegiatan").click()
        elif clean_string(df["jenis_kegiatan"][i]) == "ujian":
            page.get_by_role("option", name="Berita Acara Ujian").click()
        elif clean_string(df["jenis_kegiatan"][i]) == "bimbingan":
            page.get_by_role(
                "option",
                name="Berita Acara Pembimbingan (Konsultasi/Mentoring/Coaching)",
            ).click()

        # Tanggal
        page.get_by_placeholder("Tanggal").click()
        page.get_by_placeholder("Tanggal").type(clean_string(df["tanggal"][i]))
        page.get_by_placeholder("Tanggal").press("Escape")

        # Waktu
        page.get_by_placeholder("Waktu Selesai").click()
        for _ in range(5):
            page.keyboard.press("Backspace")
        page.get_by_placeholder("Waktu Selesai").type(
            clean_string(df["selesai"][i])
        )
        page.get_by_placeholder("Tanggal").press("Escape")

        page.get_by_placeholder("Waktu Mulai").click()
        for _ in range(5):
            page.keyboard.press("Backspace")
        page.get_by_placeholder("Waktu Mulai").type(
            clean_string(df["mulai"][i])
        )
        page.get_by_placeholder("Tanggal").press("Escape")

        # Dosen Penggerak
        page.get_by_label(DOSEN).check()

        # Tipe Penyelenggaraan
        if clean_string(df["tipe"][i]) == "offline":
            page.get_by_label("Offline").check()
        elif clean_string(df["tipe"][i]) == "online":
            page.get_by_label("Online").check()
        elif clean_string(df["tipe"][i]) == "hybrid":
            page.get_by_label("Hybrid").check()

        # Lokasi
        page.get_by_placeholder("Lokasi").fill(df["lokasi"][i])

        # Topik
        page.get_by_placeholder("Topik").fill(df["keterangan"][i])

        # File
        file_path = resolve_to_absolute_path(df["file"][i])
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        page.locator("#File").set_input_files(file_path)

        # Simpan
        page.get_by_role("button", name="Simpan").click()
        time.sleep(1)

        if i < df.shape[0] - 1:
            page.get_by_text("Tambah").first.click()

    browser.close()