# IPB Auto Logbook

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.57-green?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.11-orange?logo=qt&logoColor=white)](https://www.qt.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Multiplatform](https://github.com/insanansharyrasul/ipb_auto_logbook/actions/workflows/build.yml/badge.svg)](https://github.com/insanansharyrasul/ipb_auto_logbook/actions)
[![GPL v3 License](https://img.shields.io/badge/License-GPL_v3-blue.svg)](LICENSE)

**Automated logbook filling tool for IPB University Student Portal.** Powered by *Playwright* for browser automation, equipped with an interactive desktop interface (*PyQt6*), and a Chrome Extension (*Manifest V3*).

**Hassle-free daily logbook filling.** This project is designed for IPB students who want to batch fill activity logbooks (such as MBKM, internships, capstone, etc.) using a CSV file. You can run it as an interactive desktop GUI application, a fast terminal-based CLI script, or a *Chrome Extension* that runs directly in your active browser window without needing Python.

**Save your time.** Instead of copying daily entries one by one, simply prepare your data file, run the program, and let the system complete the forms and upload proof attachments in minutes.

---

## Table of Contents
- [Key Features](#key-features)
- [Environment Setup](#environment-setup)
- [Quick Start Guide](#quick-start-guide)
  - [Option 1: Desktop GUI (Recommended)](#option-1-desktop-gui-recommended)
  - [Option 2: Chrome Extension (Recommended)](#option-2-chrome-extension-recommended)
  - [Option 3: Command Line Interface (CLI)](#option-3-command-line-interface-cli)
- [Configuration Guide](#configuration-guide)
- [CSV Format](#csv-format)
- [Project Structure](#project-structure)
- [Maintainers & Contributors](#maintainers--contributors)
- [License](#license)

---

## Key Features

- **Accurate Automation.** Fills date, start time, end time, category type, mentor name, location, topic, and uploads proof files with high precision.
- **Three Execution Methods.** Choose the method that fits your workflow: desktop application (GUI), command-line interface (CLI), or Chrome Extension (*Manifest V3*).
- **Isolated & Secure UI.** The Chrome Extension uses a *Shadow DOM* so that the floating automation panel doesn't interfere with the layout of the IPB student portal, and all credentials are kept secure locally inside your browser.
- **Robust CSV Parsing.** Powered by the *PapaParse* library in the extension for flexible parsing that tolerates trailing spaces, empty lines, and special characters.
- **Persistent Memory.** Uses *IndexedDB* in the browser extension to safely store proof files across redirects and page loads.
- **Headless & Slow Mo Options.** Fine-tune execution speed and choose to show or hide the browser window when using the Python version.

---

## Environment Setup

### Prerequisites
To run the Python-based version (GUI / CLI), ensure you have installed:
*   **Python 3.13+**
*   *(Optional)* **`uv`** package manager for faster dependency installation and execution.

### Step 1: Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/insanansharyrasul/ipb_auto_logbook.git
cd ipb_auto_logbook
```

### Step 2: Install Dependencies
Choose one of the installation methods below (Standard Python or using `uv`):

#### Method A: Standard Python (venv + pip)
Create a virtual environment and install the required packages:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install requirements & Playwright browser driver
pip install -r requirements.txt
playwright install chromium
```

#### Method B: Using `uv` Package Manager (Fast Alternative)
If you have `uv` installed, simply run:
```bash
uv venv
uv pip install -r requirements.txt
uv run playwright install chromium
```

---

## Quick Start Guide

### Option 1: Desktop GUI (Recommended)

Run the interactive desktop application with:

#### Using Standard Python (ensure Virtual Environment is active):
```bash
python gui_app.py
```

#### Using `uv`:
```bash
uv run python gui_app.py
```

The desktop app will open with 4 main tabs:

| Tab              | Usage                                                                                           |
| :--------------- | :---------------------------------------------------------------------------------------------- |
| **Config**       | Enter portal credentials, mentor name, row number, academic semester, and select the CSV file.  |
| **Logbook Data** | View and edit your logbook entries directly inside an interactive, visual table.               |
| **Run**          | Start or stop the automation process with a visual progress bar and real-time activity logs.    |
| **About**        | Version details, project maintainers, and license.                                              |

---

### Option 2: Chrome Extension (Recommended)

If you don't want to install Python or Playwright on your computer, you can run the extension directly in your web browser:

1.  Open Google Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** in the top-right corner.
3.  Click **Load unpacked** in the top-left corner.
4.  Select the [`src/chrome-extension/`](./src/chrome-extension/) folder inside this repository.
5.  Open the IPB Student Portal in Chrome and navigate to the **Aktivitas Kampus Merdeka** page: `https://studentportal.ipb.ac.id/Kegiatan/AktivitasKampusMerdeka`.
6.  Click the floating document icon (📄) in the **top-right corner** of the page to open the control panel. (Refresh/reload the tab if the icon does not appear).
7.  Set the Dosen, Row Number, and Semester parameters, upload your logbook CSV file, and choose your proof files.
8.  Press **Mulai Pengisian**. The extension will automatically open the modal form, fill in fields, upload attachments, submit each entry, and loop through the queue in real-time.

---

### Option 3: Command Line Interface (CLI)

Run the interactive terminal-based script with:

#### Using Standard Python (ensure Virtual Environment is active):
```bash
python main.py
```

#### Using `uv`:
```bash
uv run python main.py
```

The CLI will prompt you for configuration values step-by-step:
*   Portal Username & Password (password input is masked for security).
*   Mentor name (Dosen Penggerak - must match the portal text exactly).
*   Row Number of your MBKM activity.
*   Academic Semester.
*   Path to your logbook CSV file.

---

## Configuration Guide

Use the following guidelines to enter configurations so the automator can find the correct activity row:

| Config Field            | Where to find it in the Student Portal                                                                                        | Example Input                        |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :----------------------------------- |
| **Dosen**               | Go to Activity details $\rightarrow$ Log $\rightarrow$ Tambah. Copy the full name of the Dosen Penggerak from the dropdown.   | `"Jeffrey Einstein, S.Komp., Ph.D."` |
| **Row Number (Baris)**  | Indicated in the leftmost column (`No`) of the main Activities table. Enter the ID number, not your manual count.             | `"1"`                                |
| **Semester**            | Indicated in the `Tahun Semester` column of the main Activities table. Must be written exactly as is.                         | `"2026/2027 Semester Genap"`         |

> [!IMPORTANT]
> The automation system combines the `Row Number` and `Semester` values (format: `"<Row Number> <Semester>"`) to identify and click the correct activity row on the portal table.

---

## CSV Format

The logbook CSV file must contain **8 columns** with lowercase headers.

> [!NOTE]
> Double quotes around fields are optional. Standard spreadsheet software (like Microsoft Excel or Google Sheets) will automatically wrap values in double quotes only if they contain commas or newlines. Both quoted and unquoted formats are fully supported.

| Column        | Description                                            | Example Value                                  |
| :------------ | :----------------------------------------------------- | :--------------------------------------------- |
| `tanggal`     | Date of the activity (format DD/MM/YYYY)               | `04/02/2026`                                   |
| `mulai`       | Start time (format HH:MM)                              | `15:00`                                        |
| `selesai`     | End time (format HH:MM)                                | `16:00`                                        |
| `keterangan`  | Description/topic of the daily activity                | `"Diskusi project dan pembagian jobdesk"`      |
| `file`        | Relative path to proof attachment inside [`files/`](./files/)      | `files/bukti_04_02_2026.png`                   |
| `tipe`        | Type of activity (`offline` / `online` / `hybrid`)     | `offline`                                      |
| `lokasi`      | Specific location where the activity took place        | `SC IPB`                                       |
| `berita`      | Category of activity (`kegiatan` / `ujian` / `bimbingan`)| `kegiatan`                                     |

*Supported attachment file formats: `.png`, `.jpeg`, `.jpg`, `.pdf`.*
*You can download a ready-to-use CSV template directly from the Chrome Extension panel, or use the sample [data.csv](./data.csv) file.*

---

## Project Structure

```
ipb_auto_logbook/
├── pyproject.toml          # Modern python package configuration (PEP 621)
├── uv.lock                 # Lockfile generated by uv package manager
├── pyrightconfig.json      # VS Code Pyright import paths config
├── gui_app.py              # Entry point for the Desktop GUI app
├── main.py                 # Entry point for the terminal CLI script
├── src/                    # Python and Javascript source code
│   ├── automator.py        # Core Playwright automation engine
│   ├── chrome-extension/   # Chrome Extension source code (Manifest V3)
│   │   ├── manifest.json   # Chrome Extension configuration
│   │   ├── content.js      # Shadow DOM floating UI & automation script
│   │   ├── papaparse.min.js# Third-party CSV parser
│   │   ├── popup.html      # Companion extension popup
│   │   └── popup.js        # Logic for the companion popup
│   └── gui/                # PyQt6 Desktop GUI modular components
│       ├── _constants.py   # Visual style tokens, constants, and helper texts
│       ├── _widgets.py     # Reusable custom UI components (tooltips, etc.)
│       └── ...             # Tab-specific modular implementations
├── files/                  # Directory where activity proof files should be placed
└── data.csv                # Sample logbook CSV template
```

---

## Maintainers & Contributors

### Project Founder
*   **Insan Anshary Rasul** - [@insanansharyrasul](https://github.com/insanansharyrasul)

### Contributors
*   **Aghnat Hasya Sayyidina** - [@AghnatHs](https://github.com/AghnatHs)
*   **Rafif Farras** - [@Raphcel](https://github.com/Raphcel)
*   **Raihan Putra Kirana** - [@raihanpka](https://github.com/raihanpka)

---

## License

Distributed under the **[GNU General Public License v3.0](LICENSE)**.
