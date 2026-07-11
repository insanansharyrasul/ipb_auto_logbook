<h1> IPB Auto Logbook </h1>

Automated logbook filler for [IPB University Student Portal](https://studentportal.ipb.ac.id/), powered by _[Playwright](https://playwright.dev/python/)_. Now ships with a desktop GUI (CustomTkinter).

# Table of Contents

- [Table of Contents](#table-of-contents)
- [Setup](#setup)
- [Running the App](#running-the-app)
  - [GUI (recommended)](#gui-recommended)
  - [CLI](#cli)
- [Configuration Reference](#configuration-reference)
- [CSV Format](#csv-format)
- [Project Structure](#project-structure)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

# Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 2. Prepare CSV file

Convert your `.xlsx` or Google Spreadsheet to CSV (separator `,` not `;`). See [CSV Format](#csv-format) below for column requirements.

### 3. Clone the repository

```bash
git clone https://github.com/insanansharyrasul/ipb_auto_logbook.git
cd ipb_auto_logbook
```

> [!WARNING]
> Never share your Python scripts directly with others as they may contain your username and password. Use the GUI's config fields instead credentials are never saved to disk and never sent over the network outside the student portal pages.

# Running the App

## GUI (recommended)

```bash
python gui_app.py
```

A desktop window opens with 4 tabs:

| Tab               | Purpose                                                                                                              |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Configuration** | Enter Portal username/password, Dosen, Row Number, Semester, CSV path. Hover the ⓘ icons for guidance on each field. |
| **Logbook Data**  | Edit your logbook entries in a table. Load CSV, add/delete rows, browse for files.                                   |
| **Run**           | Start/stop automation with live progress bar and log output.                                                         |
| **About**         | Version info, maintainers, and license.                                                                              |

Fill in the Configuration tab, load your CSV in Logbook Data, then switch to Run and start.

## CLI

```bash
python main.py
```

Edit variables at the top of `main.py` first:

| Variable     | Description                                                       |
| ------------ | ----------------------------------------------------------------- |
| `df`         | Path to your `.csv` file (default: `"data.csv"`)                  |
| `DOSEN`      | Dosen Penggerak name exactly as shown in the portal               |
| `ROW_NUMBER` | The **No** column value of your activity row (not a manual count) |
| `SEMESTER`   | Academic year & semester, e.g. `"2026/2027 Semester Genap"`       |

You'll be prompted for username and password in the terminal at runtime.

# Configuration Reference

| Field          | Where to find it                                                                                                                                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dosen**      | Student Portal → Kemahasiswaan → Aktivitas → Log (list icon) → Tambah. Copy the name exactly from the "Dosen Penggerak" checkbox, e.g. `"Jeffrey Einstein, S.Komp., Ph.D."`. NRP is optional. |
| **Row Number** | Kemahasiswaan → Aktivitas page. The number in the leftmost `No` column of your target activity row. Use the displayed number, not a manual row count.                                         |
| **Semester**   | Same page, the `Tahun Semester` column. Must match exactly, e.g. `"2026/2027 Semester Genap"`.                                                                                                |

> `ROW_NUMBER` and `SEMESTER` are combined to locate the correct row on the Aktivitas table (`"<ROW_NUMBER> <SEMESTER>"`).

# CSV Format

8 columns, all values lowercase:

| Column       | Description                        | Example                |
| ------------ | ---------------------------------- | ---------------------- |
| `tanggal`    | Date (DD/MM/YYYY)                  | `12/04/2026`           |
| `mulai`      | Start time (HH:MM)                 | `08:00`                |
| `selesai`    | End time (HH:MM)                   | `10:00`                |
| `keterangan` | Description / topic                | `Observasi dan Survei` |
| `file`       | Relative path under `files/`       | `files/bukti.png`      |
| `tipe`       | `offline` / `online` / `hybrid`    | `offline`              |
| `lokasi`     | Location                           | `Kos`                  |
| `berita`     | `kegiatan` / `ujian` / `bimbingan` | `kegiatan`             |

Accepted file formats for upload: `.png`, `.jpeg`, `.jpg`, `.pdf`. The app resolves relative paths to absolute paths automatically.

See [data.csv](data.csv) for a complete example.

# Project Structure

```
├── gui_app.py              # Desktop GUI entry point
├── main.py                 # CLI entry point
├── src/
│   ├── automator.py        # Playwright automation core
│   └── gui/                # GUI components (modular mixins)
│       ├── _constants.py   # Shared constants & info texts
│       ├── _widgets.py     # Reusable widgets (info tooltips)
│       ├── _config_mixin.py
│       ├── _data_mixin.py
│       ├── _run_mixin.py
│       └── _about_mixin.py
├── files/                  # Upload files directory
├── data.csv                # Example CSV input
└── requirements.txt
```

# Contributing

The browser engine can be switched from `chromium` to `firefox` in `src/automator.py`. See the [Playwright documentation](https://playwright.dev/python/docs/intro) for details.

GUI components are organized as mixins in `src/gui/` with each tab is self-contained. To add a new tab, create a new mixin and inherit it in `LogbookApp`.

# License

[GNU General Public License v3.0](LICENSE)
