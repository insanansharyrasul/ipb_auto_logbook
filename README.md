# IPB Auto Logbook

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.57-green?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.11-orange?logo=qt&logoColor=white)](https://www.qt.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Multiplatform Executables](https://github.com/insanansharyrasul/ipb_auto_logbook/actions/workflows/build-windows.yml/badge.svg)](https://github.com/insanansharyrasul/ipb_auto_logbook/actions)
[![GPL v3 License](https://img.shields.io/badge/License-GPL_v3-blue.svg)](LICENSE)

*Alat pengisi logbook otomatis untuk Portal Mahasiswa IPB University.* Ditenagai oleh *Playwright* untuk otomasi browser dan dilengkapi dengan antarmuka desktop (*PyQt6*) serta ekstensi Chrome (*Manifest V3*).

**Otomasi pengisian harian tanpa repot.** Proyek ini dirancang untuk mahasiswa IPB yang ingin mengisi logbook kegiatan (seperti MBKM, magang, dll.) secara massal menggunakan berkas CSV. Anda dapat menjalankannya sebagai aplikasi desktop GUI yang interaktif, skrip terminal CLI yang cepat, atau *Chrome Extension* (*browser extension*) yang berjalan langsung di *browser* aktif Anda tanpa perlu menyentuh kode Python.

*Menghemat waktu Anda.* Alih-alih menyalin entri kegiatan satu per satu setiap hari, cukup persiapkan berkas data Anda, jalankan program, dan biarkan sistem menyelesaikan pengisian beserta *upload* lampiran berkas bukti dalam hitungan menit.

---

## Table of Contents (TOC)
- [Fitur Utama](#fitur-utama)
- [Setup Lingkungan](#setup-lingkungan)
- [Panduan Memulai Cepat (Quick Start)](#panduan-memulai-cepat-quick-start)
  - [Opsi 1: Desktop GUI](#opsi-1-desktop-gui)
  - [Opsi 2: Chrome Extension (Browser Companion - Sangat Direkomendasikan)](#opsi-2-chrome-extension-browser-companion---sangat-direkomendasikan)
  - [Opsi 3: Command Line Interface (CLI)](#opsi-3-command-line-interface-cli)
- [Panduan Konfigurasi](#panduan-konfigurasi)
- [Format CSV](#format-csv)
- [Struktur Proyek](#struktur-proyek)
- [Pemelihara & Kontributor](#pemelihara--kontributor)
- [Lisensi](#lisensi)

---

## Fitur Utama

- **Otomasi Akurat.** Mengisi tanggal, waktu mulai, waktu selesai, jenis berita acara, dosen penggerak, lokasi, topik kegiatan, hingga melakukan *upload* berkas bukti secara presisi.
- **Tiga Metode Eksekusi.** Pilih metode yang paling nyaman bagi Anda: aplikasi desktop visual (GUI), antarmuka baris perintah (CLI), atau ekstensi Chrome (*Manifest V3*).
- **Isolasi UI & Aman.** Ekstensi Chrome menggunakan *Shadow DOM* sehingga tampilan panel otomasi tidak merusak visual portal mahasiswa IPB, dan seluruh kredensial Anda tersimpan aman secara lokal di *browser* Anda.
- **Dukungan Pengurai Tangguh.** Menggunakan *library* *PapaParse* pada ekstensi untuk *parsing* CSV yang toleran terhadap spasi, baris kosong, maupun karakter khusus.
- **Penyimpanan Berkas Lintas Muatan.** Menggunakan *IndexedDB* pada ekstensi untuk menyimpan berkas bukti dalam memori *browser* secara aman melewati *redirect* halaman.
- **Opsi Headless & Slow Mo.** Sesuaikan kecepatan eksekusi otomasi dan pilih untuk menampilkan atau menyembunyikan jendela *browser* saat menggunakan versi Python.

---

## Setup Lingkungan

### Prasyarat
Untuk menjalankan aplikasi versi Python (GUI / CLI), pastikan Anda telah memasang:
*   **Python 3.13+**
*   *(Opsional)* Manajer paket **`uv`** untuk instalasi dan eksekusi yang lebih cepat.

### Langkah 1: Clone Repositori
*Clone* proyek ini ke komputer lokal Anda:
```bash
git clone https://github.com/insanansharyrasul/ipb_auto_logbook.git
cd ipb_auto_logbook
```

### Langkah 2: Instalasi Dependensi
Pilih salah satu metode instalasi di bawah ini (metode standar Python atau menggunakan `uv`):

#### Metode A: Standar Python (venv + pip)
Buat virtual environment dan pasang dependensi menggunakan modul bawaan Python:
```bash
# Membuat virtual environment
python3 -m venv .venv

# Mengaktifkan virtual environment
# Di macOS / Linux:
source .venv/bin/activate
# Di Windows (Command Prompt):
.venv\Scripts\activate.bat
# Di Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Memasang dependensi & browser driver Playwright
pip install -r requirements.txt
playwright install chromium
```

#### Metode B: Menggunakan manajer paket `uv` (Alternatif Cepat)
Jika Anda memiliki `uv` terpasang, cukup jalankan perintah berikut:
```bash
uv venv
uv pip install -r requirements.txt
uv run playwright install chromium
```

---

## Panduan Memulai Cepat (Quick Start)

### Opsi 1: Desktop GUI

Jalankan aplikasi desktop interaktif dengan perintah:

#### Menggunakan Python Standar (Pastikan Virtual Environment Aktif):
```bash
python gui_app.py
```

#### Alternatif Menggunakan `uv`:
```bash
uv run python gui_app.py
```

Jendela aplikasi desktop akan terbuka dengan 4 tab utama:

| Tab              | Kegunaan                                                                                                |
| :--------------- | :------------------------------------------------------------------------------------------------------ |
| **Konfigurasi**  | Memasukkan *username*/*password* portal, nama Dosen, Nomor Baris kegiatan, Semester, dan berkas CSV.    |
| **Data Logbook** | Melihat dan menyunting langsung data logbook Anda dalam bentuk tabel secara visual.                     |
| **Jalankan**     | Memulai atau menghentikan proses otomasi dengan indikator progres dan log aktivitas *real-time*.        |
| **Tentang**      | Informasi versi, pemelihara proyek, dan lisensi.                                                        |

---

### Opsi 2: Chrome Extension (Browser Companion - Sangat Direkomendasikan)

Jika Anda tidak ingin menginstal Python atau Playwright di komputer Anda, Anda bisa menggunakan ekstensi Chrome yang berjalan langsung di *browser* aktif Anda:

1.  Buka Google Chrome dan navigasikan ke `chrome://extensions/`.
2.  Aktifkan **Mode Pengembang** (*Developer mode*) di pojok kanan atas.
3.  Klik **Load unpacked** di pojok kiri atas.
4.  Pilih direktori folder `extension/` di dalam repositori ini (`ipb_auto_logbook/extension`).
5.  Buka halaman Portal Mahasiswa IPB pada bagian **Aktivitas Kampus Merdeka**: `https://studentportal.ipb.ac.id/Kegiatan/AktivitasKampusMerdeka`.
6.  Klik ikon dokumen berwarna biru di pojok kanan bawah halaman untuk membuka panel kontrol.
7.  Masukkan nama Dosen, nomor baris, semester, kredensial login (opsional untuk *auto-login*), *upload* berkas CSV, dan pilih berkas bukti fisik Anda.
8.  Tekan **Mulai Pengisian**. Ekstensi akan otomatis *login*, membuka form, mengisi kolom, melakukan *upload* bukti, mengirim formulir, dan mengulangi proses tersebut untuk baris berikutnya.

---

### Opsi 3: Command Line Interface (CLI)

Jalankan skrip berbasis terminal interaktif dengan perintah:

#### Menggunakan Python Standar (Pastikan Virtual Environment Aktif):
```bash
python main.py
```

#### Alternatif Menggunakan `uv`:
```bash
uv run python main.py
```

Sistem akan menanyakan parameter konfigurasi langsung dari terminal secara runtut:
*   *Username* & *Password* Portal (masukan kata sandi disembunyikan untuk keamanan).
*   Nama Dosen Penggerak (harus sama persis dengan yang tertera di portal).
*   Nomor Baris (*Row Number*) kegiatan MBKM Anda.
*   Semester akademik aktif.
*   Path menuju berkas CSV data logbook Anda.

---

## Panduan Konfigurasi

Berikut acuan untuk mengisi kolom konfigurasi agar otomasi dapat menemukan baris kegiatan yang tepat di portal:

| Bidang Konfigurasi             | Lokasi Pengambilan Data di Portal Mahasiswa                                                                                          | Contoh Masukan                       |
| :----------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------- |
| **Dosen**                      | Masuk ke detail Aktivitas $\rightarrow$ Log $\rightarrow$ Tambah. Salin nama lengkap Dosen Penggerak secara presisi dari daftar pilihan yang tersedia. | `"Jeffrey Einstein, S.Komp., Ph.D."` |
| **Nomor Baris (*Row Number*)** | Tertera pada tabel utama halaman Aktivitas. Ambil nilai angka pada kolom paling kiri (`No`), bukan urutan baris manual Anda.          | `"1"`                                |
| **Semester**                   | Tertera pada kolom `Tahun Semester` di tabel utama halaman Aktivitas. Harus ditulis sama persis.                                     | `"2026/2027 Semester Genap"`         |

> [!IMPORTANT]
> Sistem otomasi akan menggabungkan nilai `Nomor Baris` dan `Semester` (format: `"<Nomor Baris> <Semester>"`) untuk mencari dan mengklik baris aktivitas yang tepat pada tabel portal mahasiswa.

---

## Format CSV

Berkas data logbook harus memiliki **8 kolom** dengan penulisan huruf kecil (*lowercase*) pada tajuk (*header*) kolomnya:

| Kolom        | Deskripsi                                               | Contoh Nilai                              |
| :----------- | :------------------------------------------------------ | :---------------------------------------- |
| `tanggal`    | Tanggal kegiatan (format DD/MM/YYYY)                    | `16/07/2026`                              |
| `mulai`      | Waktu mulai kegiatan (format HH:MM)                     | `08:00`                                   |
| `selesai`    | Waktu selesai kegiatan (format HH:MM)                   | `10:00`                                   |
| `keterangan` | Deskripsi / ringkasan kegiatan harian                   | `Observasi dan Survei Kebutuhan Pengguna` |
| `file`       | Path relatif berkas bukti di dalam folder `files/`      | `files/bukti.png`                         |
| `tipe` | Pilihan tipe kegiatan (*offline* / *online* / *hybrid*) | `offline` |
| `lokasi`     | Lokasi spesifik tempat kegiatan dilakukan               | `Kos` / `Kantor Magang`                   |
| `berita`     | Jenis berita acara (*kegiatan* / *ujian* / *bimbingan*) | `kegiatan`                                |

*Format file bukti yang didukung oleh portal IPB: `.png`, `.jpeg`, `.jpg`, `.pdf`.*
*Download template CSV siap pakai langsung dari panel kontrol ekstensi Chrome.*

---

## Struktur Proyek

```
ipb_auto_logbook/
├── pyproject.toml          # Konfigurasi dependensi proyek modern (PEP 621)
├── uv.lock                 # Berkas penguncian dependensi yang dihasilkan oleh uv
├── pyrightconfig.json      # Konfigurasi import paths Pylance/Pyright untuk VS Code
├── gui_app.py              # Titik masuk (entry point) aplikasi desktop GUI
├── main.py                 # Titik masuk (entry point) aplikasi terminal CLI
├── extension/              # Sumber kode untuk Chrome Extension
│   ├── manifest.json       # Konfigurasi Manifest V3 Chrome Extension
│   ├── content.js          # Skrip otomasi halaman & UI melayang dalam Shadow DOM
│   ├── papaparse.min.js    # Pustaka pihak ketiga untuk mengurai berkas CSV secara lokal
│   └── icons/              # Ikon ekstensi menggunakan Logo IPB University
├── src/                    # Kode inti logika Python
│   ├── automator.py        # Core mesin otomasi berbasis Playwright
│   └── gui/                # Struktur modular visual PyQt6
│       ├── _constants.py   # Konstanta bersama dan panduan informasi teks
│       ├── _widgets.py     # Widget visual yang dapat digunakan kembali (seperti tooltip)
│       └── ...             # Mixin kode modular PyQt6 per tab halaman
├── files/                  # Tempat berkas lampiran bukti kegiatan diletakkan
└── data.csv                # Contoh berkas input logbook awal Anda
```

---

## Pemelihara & Kontributor

### Penggagas Project Utama
*   **Insan Anshary Rasul** - [@insanansharyrasul](https://github.com/insanansharyrasul)

### Contributor
*   **Aghnat Hasya Sayyidina** - [@AghnatHs](https://github.com/AghnatHs)
*   **Rafif Farras** - [@Raphcel](https://github.com/Raphcel)
*   **Raihan Putra Kirana** - [@raihanpka](https://github.com/raihanpka)

---

## Lisensi

Didistribusikan di bawah **[Lisensi GNU General Public License v3.0](LICENSE)**.
