"""IPB AUTO LOGBOOK"""

from getpass import getpass
from pathlib import Path

import time
from playwright.sync_api import sync_playwright
import pandas as pd

CURRENT_DIR = Path(__file__).parent

def clean_string(string):
    """Cleans a string by converting it to lowercase and removing spaces."""
    string = string.lower().replace(" ", "")
    return string

# Input Data (Becareful of password)
# ! Password
df = pd.read_csv("data.csv")
USERNAME = str(input("Username: "))
PASSWORD = str(getpass("Password: "))
DOSEN = "dosen"  # Example: "Jeffrey Einstein, S.Komp., Ph.D."
ROW_NUMBER = "row_number"  # Example: "1" for the first row, or "2" for the second row
SEMESTER = "YYYY/YYYY Semester Ganjil/Genap"  # Example: "2023/2024 Semester Genap"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page()
    page.goto("https://studentportal.ipb.ac.id/Account/Login")
    page.get_by_placeholder("Username").click()

    # Login
    page.get_by_placeholder("Username").fill(USERNAME)
    page.get_by_placeholder("Password").fill(PASSWORD)
    page.get_by_role("button", name="Masuk").click()

    time.sleep(1)
    page.get_by_role("link", name=" Kemahasiswaan ").click()
    time.sleep(1)
    page.get_by_role("link", name=" Aktivitas").click()
    page.get_by_role("row", name=f"{ROW_NUMBER} {SEMESTER}").get_by_role("link").nth(
        2
    ).click()
    page.get_by_text("Tambah").click()

    # Logbook

    for i in range(df.shape[0]):
        # Tanggal
        page.get_by_placeholder("Tanggal").click()
        page.get_by_placeholder("Tanggal").type(clean_string(df["tanggal"][i]))
        page.get_by_placeholder("Tanggal").press("Escape")

        # Waktu
        page.get_by_placeholder("Waktu Selesai").click()
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.get_by_placeholder("Waktu Selesai").type(clean_string(df["selesai"][i]))
        page.get_by_placeholder("Tanggal").press("Escape")
        page.get_by_placeholder("Waktu Mulai").click()
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.keyboard.press("Backspace")
        page.get_by_placeholder("Waktu Mulai").type(clean_string(df["mulai"][i]))
        page.get_by_placeholder("Tanggal").press("Escape")

        # Berita Acara Kegiatan
        page.get_by_role("textbox", name="-- Pilih --").click()

        if clean_string(df["berita"][i]) == "kegiatan":
            page.get_by_role("option", name="Berita Acara Kegiatan").click()
        elif clean_string(df["berita"][i]) == "ujian":
            page.get_by_role("option", name="Berita Acara Ujian").click()
        elif clean_string(df["berita"][i]) == "bimbingan":
            page.get_by_role(
                "option",
                name="Berita Acara Pembimbingan (Konsultasi/Mentoring/Coaching)",
            ).click()

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
        page.locator("#File").click()
        time.sleep(1)
        FILE_PATH = str(CURRENT_DIR / df["file"][i])
        page.locator("#File").set_input_files(FILE_PATH)

        page.get_by_role("button", name="Simpan").click()
        time.sleep(1)
        page.get_by_text("Tambah").first.click()
