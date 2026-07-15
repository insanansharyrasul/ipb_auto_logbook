"""IPB Auto Logbook — CLI entry point.

Thin terminal front-end over the shared automation core in src/automator.py.
Run with:  python main.py
"""

from getpass import getpass

from src.automator import LogbookAutomator, LogbookConfig


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def main() -> None:
    print("IPB Auto Logbook (CLI)\n")
    config = LogbookConfig(
        username=_prompt("Username"),
        password=getpass("Password: "),
        dosen=_prompt("Dosen Penggerak (exact name)"),
        row_number=_prompt("Row Number"),
        semester=_prompt("Semester (e.g. 2026/2027 Semester Genap)"),
        csv_path=_prompt("CSV file", "data.csv"),
    )

    automator = LogbookAutomator(
        config,
        progress_callback=lambda cur, total, msg: print(f"[{cur}/{total}] {msg}"),
        log_callback=print,
    )

    ok = automator.run()
    print("\n✅ Done." if ok else "\n❌ Failed. See messages above.")


if __name__ == "__main__":
    main()
