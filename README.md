<h1> IPB-Auto-Logbook </h1>

Ini adalah source code untuk mengisi logbook IPB secara automatis dengan menggunakan *[Playwright](https://playwright.dev/python/)* (Python) dan CSV sebagai input logbook

# Table of Content
- [Table of Content](#table-of-content)
- [Problems](#problems)
- [Setup](#setup)
- [Running the script](#running-the-script)
- [What can i change on the script?](#what-can-i-change-on-the-script)

# Problems

Sayangnya, tidak diketahui apakah proses automasi ini akan merusak [studentportal.ipb.ac.id](studentportal.ipb.ac.id),
sehingga repository ini bisa ditutup kapanpun. Selain itu, script ini masih dalam pengembangan yang kemungkinan masih memiliki bug.
Berikut ini masalah yang masih dipertimbangkan:
1. "Waktu Mulai" dan "Waktu Selesai" yang terisi automatis dengan waktu saat ini
2. Belum diuji coba di OS selain Linux (Ubuntu)
3. Pengolahan data untuk diinput harus berupa `.csv` dengan aturan ketat
4. Dokumentasi harus berbentuk filepath, menyebabkan "dua kali kerja" (Bisa diakali, dengan menyiapkan folder dahulu, lalu meng-copy path nya saja ke Excel/Spreadsheet)

&#x26a0;&#xfe0f; **Hati Hati! Bagi yang langsung meng-copy script yang sudah diubah isinya dan menyebarluaskannya, karena terdapat data penting seperti `password` yang terdapat dalam script.**

# Setup

Apa yang perlu diinstal?
* Python (3.10.12)
* Install packages 
    * Manual:
        * Playwright
            ```
            pip3 install playwright
            pip3 install pytest-playwright
            playwright install
            ```
        * Pandas
            ```
            pip3 install pandas
            ```
    * `requirements.txt`:
        ```
        pip install -r requirements.txt
        ```
* File CSV

    File CSV bisa didapatkan dengan convert `.xlsx` menjadi `.csv` atau google spreadsheet dengan mendownloadnya dalam bentuk CSV dan pastikan separator dalam bentuk `,` bukan `;`.

    Kolom dari file csv harus berisikan:

    1. `tanggal` (Tanggal Kegiatan, format DD/MM/YY)
    2. `mulai` (Jam Mulai HH:MM)
    3. `selesai` (Jam Mulai HH:MM)
    4. `keterangan` 
    5. `file` (Copy full path, sesuaikan dengan OS)
    6. `tipe` (memiliki isi khusus)
       1. offline
       2. online
       3. hybrid
    7. `lokasi`
    8. `berita` (memiliki is khusus)
       1. kegiatan
       2. ujian
       3. bimbingan

    Semua kolom dan isi khusus harus lowercase, lebih jelas, lihat [data.csv](data.csv)

* Clone Repository ini
    ```
    git clone ~
    ```

* Python Script
  
    Di bagian paling atas, terdapat variabel yang dapat diganti, menyesuaikan data.
    1. `df` untuk input file `.csv` dan harus berada di directory yang sama
    2. `username` untuk Username IPB
    3. `password` untuk password
    4. `dosen` untuk dosen pembimbing

# Running the script

Sesuaikan directory dan jalankan:
```
python3 main.py
```
Script akan berjalan dengan membuka chromium.

# What can i change on the script?

Script dapat diubah sesuai kebutuhan dengan mempelajari dokumentasi [Playwright documentation](https://playwright.dev/python/docs/intro) 

Browser yang berada pada variable `browser` juga bisa diubah dari `chromium` menjadi `firefox`
