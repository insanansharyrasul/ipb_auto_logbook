"""Shared constants used across GUI tabs."""

from __future__ import annotations

TIPE_VALUES: list[str] = ["offline", "online", "hybrid"]
BERITA_VALUES: list[str] = ["kegiatan", "ujian", "bimbingan"]
CSV_COLUMNS: list[str] = [
    "tanggal",
    "mulai",
    "selesai",
    "keterangan",
    "file",
    "tipe",
    "lokasi",
    "berita",
]

DOSEN_INFO: str = (
    "Nama Dosen Penggerak dari Student Portal.\n"
    "Kemahasiswaan → Aktivitas → Log (ikon list) → Tambah.\n"
    "Contoh: 'Jeffrey Einstein, S.Komp., Ph.D.'."
)
ROW_NUMBER_INFO: str = "Angka di kolom 'No' pada halaman Kemahasiswaan → Aktivitas."
SEMESTER_INFO: str = (
    "Tahun & semester sesuai kolom 'Tahun Semester'.\n"
    "Contoh: '2026/2027 Semester Genap'."
)

APP_VERSION: str = "1.0.0"

APP_MAINTAINERS: list[str] = [
    "Insan Anshary Rasul (https://github.com/insanansharyrasul)",
    "Aghnat Hasya Sayyidina (https://github.com/aghnaths)",
    "Rafif Muhammad Faras (https://github.com/Raphcel)",
]

APP_DONATORS: list[str] = ["Walid Nadirul Ahnaf (https://github.com/walidan-nadilaw)"]
