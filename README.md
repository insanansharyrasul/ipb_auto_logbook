# IPB-Auto-Logbook

Ini adalah source code untuk mengisi logbook IPB secara otomatis menggunakan **[Playwright](https://playwright.dev/python/)** (Python) dengan file CSV sebagai input logbook.

# Table of Content

* [Table of Content](#table-of-content)
* [Problems](#problems)
* [Setup](#setup)
* [Running the Script](#running-the-script)
* [Contributing](#contributing)

# Problems

Sayangnya, belum diketahui apakah proses automasi ini akan berdampak pada **studentportal.ipb.ac.id**, sehingga repository ini bisa saja ditutup kapan pun. Selain itu, script ini masih dalam tahap pengembangan sehingga kemungkinan masih memiliki bug.

Beberapa keterbatasan yang masih perlu diperhatikan:

1. Data input harus berupa file `.csv` dengan format yang telah ditentukan.
2. Dokumentasi harus berupa filepath sehingga pengguna perlu menyiapkan file dokumentasi terlebih dahulu (misalnya dengan membuat folder khusus, lalu menyalin path file ke spreadsheet).

> [!WARNING]
> Jika ingin mengubah script Python secara langsung dan membagikannya kepada orang lain, pastikan tidak ada informasi sensitif seperti username atau password yang ikut terbagikan.

# Setup

## Yang perlu diinstal

* Python (3.10.12)

* Install package

  **Manual**

  **Playwright**

  ```bash
  pip3 install playwright
  pip3 install pytest-playwright
  playwright install
  ```

  **Pandas**

  ```bash
  pip3 install pandas
  ```

  **Menggunakan requirements.txt**

  ```bash
  pip install -r requirements.txt
  ```

> Jika Playwright tidak dapat di-install melalui terminal, silakan ikuti panduan resmi di https://playwright.dev/python/docs/intro.

## File CSV

File CSV dapat dibuat dengan:

* Mengubah file `.xlsx` menjadi `.csv`.
* Mengunduh Google Spreadsheet sebagai file CSV.

Pastikan separator yang digunakan adalah **`,`** dan bukan **`;`**.

Kolom CSV harus memiliki urutan berikut:

| Kolom            | Keterangan                                                                                                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tanggal`        | Tanggal kegiatan (format `DD/MM/YY`)                                                                                                                                              |
| `mulai`          | Jam mulai (`HH:MM`)                                                                                                                                                               |
| `selesai`        | Jam selesai (`HH:MM`)                                                                                                                                                             |
| `keterangan`     | Deskripsi kegiatan                                                                                                                                                                |
| `file`           | Path file dokumentasi. Gunakan format seperti `files/example_file.pdf`. Script akan mengubahnya menjadi absolute path menggunakan `pathlib`.                                      |
| `tipe`           | Jenis pelaksanaan kegiatan. Nilai yang diperbolehkan: `offline`, `online`, `hybrid`.                                                                                              |
| `jenis_kegiatan` | Jenis aktivitas yang akan dipilih pada Student Portal. Nilai harus sesuai dengan pilihan yang tersedia pada portal (contoh: `rutin`, `kepanitiaan`, dan lainnya sesuai dropdown). |
| `lokasi`         | Lokasi kegiatan                                                                                                                                                                   |
| `berita`         | Jenis berita acara. Nilai yang diperbolehkan: `kegiatan`, `ujian`, `bimbingan`.                                                                                                   |

Semua nama kolom dan nilai khusus harus menggunakan huruf **lowercase**.

Contoh dapat dilihat pada file `data.csv`.

> **Catatan**
>
> Student Portal hanya menerima file dokumentasi dengan format:
>
> * `.png`
> * `.jpg`
> * `.jpeg`
> * `.pdf`
>
> File `.txt` pada repository ini hanya digunakan sebagai contoh.

## Clone Repository

```bash
git clone https://github.com/insanansharyrasul/ipb_auto_logbook
```

## Konfigurasi Script

Di bagian paling atas `main.py` terdapat beberapa variabel yang **wajib** diubah terlebih dahulu.

| Variabel     | Isi                               | Cara mendapatkannya                                                                                                                                                            |
| ------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `df`         | File `.csv` berisi data logbook   | Ganti `"data.csv"` jika menggunakan nama file lain. File harus berada pada folder yang sama dengan `main.py`.                                                                  |
| `DOSEN`      | Nama Dosen Penggerak              | Buka aktivitas target di Student Portal → **Kemahasiswaan → Aktivitas → Log (ikon list) → Tambah**. Salin nama persis seperti yang tertulis pada checkbox **Dosen Penggerak**. |
| `ROW_NUMBER` | Nomor pada kolom **No** aktivitas | Ambil dari halaman **Kemahasiswaan → Aktivitas** pada kolom paling kiri.                                                                                                       |
| `SEMESTER`   | Tahun & semester aktivitas        | Harus sama persis dengan yang tampil pada kolom **Tahun Semester**.                                                                                                            |

> `ROW_NUMBER` dan `SEMESTER` digunakan bersama untuk menemukan aktivitas yang benar (`"<ROW_NUMBER> <SEMESTER>"`), sehingga keduanya harus sesuai dengan yang ada di Student Portal.

## Input Informasi Akun

Setelah konfigurasi selesai, jalankan script.

Masukkan **username** dan **password** Student Portal ketika diminta melalui terminal. Password tidak akan ditampilkan saat diketik dan tidak disimpan di dalam source code.

# Running the Script

Jalankan script dengan:

```bash
python3 main.py
```

Script akan membuka browser Chromium dan mulai mengisi logbook secara otomatis.

# Contributing

Script dapat dimodifikasi sesuai kebutuhan dengan mempelajari dokumentasi resmi Playwright:

https://playwright.dev/python/docs/intro

Browser yang digunakan juga dapat diubah dari `chromium` menjadi `firefox`.

Apabila menemukan bug atau memiliki usulan perbaikan, silakan membuat diskusi pada halaman **Issues** repository.
