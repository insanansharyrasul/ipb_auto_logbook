"""QtQuick-facing controller and logbook row model."""

from __future__ import annotations

import csv
from datetime import datetime

from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QThread,
    QUrl,
    Qt,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from src.automator import LogbookAutomator, LogbookConfig, resolve_to_absolute_path
from src.gui._constants import (
    APP_DONATORS,
    APP_MAINTAINERS,
    APP_VERSION,
    BERITA_VALUES,
    CSV_COLUMNS,
    DOSEN_INFO,
    ROW_NUMBER_INFO,
    SEMESTER_INFO,
    TIPE_VALUES,
)


class LogbookRowsModel(QAbstractListModel):
    """Editable list of CSV rows, one QAbstractListModel role per column."""

    countChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict[str, str]] = []

    # -- QAbstractListModel ------------------------------------------------

    def roleNames(self) -> dict[int, bytes]:  # noqa: N802 (Qt override)
        return {
            int(Qt.ItemDataRole.UserRole) + i: name.encode()
            for i, name in enumerate(CSV_COLUMNS)
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def data(self, index: QModelIndex, role: int = 0):
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return None
        col = role - int(Qt.ItemDataRole.UserRole)
        if 0 <= col < len(CSV_COLUMNS):
            return self._rows[index.row()].get(CSV_COLUMNS[col], "")
        return None

    def setData(self, index: QModelIndex, value, role: int = 0) -> bool:  # noqa: N802
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return False
        col = role - int(Qt.ItemDataRole.UserRole)
        if not 0 <= col < len(CSV_COLUMNS):
            return False
        self._rows[index.row()][CSV_COLUMNS[col]] = str(value)
        self.dataChanged.emit(index, index, [role])
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    # -- QML API -----------------------------------------------------------

    @pyqtProperty(int, notify=countChanged)
    def count(self) -> int:
        return len(self._rows)

    @pyqtSlot(int, str, str)
    def setField(self, row: int, column: str, value: str) -> None:
        if column not in CSV_COLUMNS or not 0 <= row < len(self._rows):
            return
        self.setData(self.index(row, 0), value, self._role(column))

    @pyqtSlot()
    def addRow(self) -> None:
        self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
        self._rows.append(
            {
                "tanggal": "",
                "mulai": "",
                "selesai": "",
                "keterangan": "",
                "file": "",
                "tipe": "offline",
                "lokasi": "",
                "berita": "kegiatan",
            }
        )
        self.endInsertRows()
        self.countChanged.emit()

    @pyqtSlot()
    def removeLastRow(self) -> None:
        if not self._rows:
            return
        last = len(self._rows) - 1
        self.beginRemoveRows(QModelIndex(), last, last)
        self._rows.pop()
        self.endRemoveRows()
        self.countChanged.emit()

    # -- Python API --------------------------------------------------------

    def load(self, rows: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._rows = []
        for row in rows:
            self._rows.append(
                {
                    col: str(row.get(col) or "")
                    or ("offline" if col == "tipe" else "kegiatan" if col == "berita" else "")
                    for col in CSV_COLUMNS
                }
            )
        self.endResetModel()
        self.countChanged.emit()

    def to_rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self._rows]

    @staticmethod
    def _role(column: str) -> int:
        return int(Qt.ItemDataRole.UserRole) + CSV_COLUMNS.index(column)


class _RunWorker(QThread):
    """Runs the automator off the UI thread, relaying its callbacks as signals."""

    progress = pyqtSignal(int, int, str)
    log = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, config: LogbookConfig) -> None:
        super().__init__()
        self.automator = LogbookAutomator(
            config=config,
            progress_callback=self.progress.emit,
            log_callback=self.log.emit,
        )

    def run(self) -> None:
        try:
            self.done.emit(self.automator.run())
        except Exception as exc:  # pragma: no cover - defensive thread boundary
            self.log.emit(f"✗ Fatal error: {exc}")
            self.done.emit(False)


class AppController(QObject):
    """Exposes configuration, CSV data, and run state to the QML UI."""

    configLoaded = pyqtSignal()
    usernameChanged = pyqtSignal()
    passwordChanged = pyqtSignal()
    dosenChanged = pyqtSignal()
    rowNumberChanged = pyqtSignal()
    semesterChanged = pyqtSignal()
    csvPathChanged = pyqtSignal()
    headlessChanged = pyqtSignal()
    slowMoChanged = pyqtSignal()
    runningChanged = pyqtSignal()
    stoppingChanged = pyqtSignal()
    statusTextChanged = pyqtSignal()
    statusKindChanged = pyqtSignal()
    progressChanged = pyqtSignal()
    logTextChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._username = ""
        self._password = ""
        self._dosen = ""
        self._row_number = ""
        self._semester = ""
        self._csv_path = "data.csv"
        self._headless = False
        self._slow_mo = 200
        self._running = False
        self._stopping = False
        self._status_text = "Ready"
        self._status_kind = "idle"
        self._progress_current = 0
        self._progress_total = 0
        self._log_text = ""
        self._worker: _RunWorker | None = None
        self._rows_model = LogbookRowsModel()

    @pyqtProperty(QObject, constant=True)
    def rows(self) -> LogbookRowsModel:
        return self._rows_model

    # ------------------------------------------------------------------
    # Configuration properties
    # ------------------------------------------------------------------

    @pyqtProperty(str, notify=usernameChanged)
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if self._username != value:
            self._username = value
            self.usernameChanged.emit()

    @pyqtProperty(str, notify=passwordChanged)
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        if self._password != value:
            self._password = value
            self.passwordChanged.emit()

    @pyqtProperty(str, notify=dosenChanged)
    def dosen(self) -> str:
        return self._dosen

    @dosen.setter
    def dosen(self, value: str) -> None:
        if self._dosen != value:
            self._dosen = value
            self.dosenChanged.emit()

    @pyqtProperty(str, notify=rowNumberChanged)
    def rowNumber(self) -> str:
        return self._row_number

    @rowNumber.setter
    def rowNumber(self, value: str) -> None:
        if self._row_number != value:
            self._row_number = value
            self.rowNumberChanged.emit()

    @pyqtProperty(str, notify=semesterChanged)
    def semester(self) -> str:
        return self._semester

    @semester.setter
    def semester(self, value: str) -> None:
        if self._semester != value:
            self._semester = value
            self.semesterChanged.emit()

    @pyqtProperty(str, notify=csvPathChanged)
    def csvPath(self) -> str:
        return self._csv_path

    @csvPath.setter
    def csvPath(self, value: str) -> None:
        if self._csv_path != value:
            self._csv_path = value
            self.csvPathChanged.emit()

    @pyqtProperty(bool, notify=headlessChanged)
    def headless(self) -> bool:
        return self._headless

    @headless.setter
    def headless(self, value: bool) -> None:
        if self._headless != value:
            self._headless = value
            self.headlessChanged.emit()

    @pyqtProperty(int, notify=slowMoChanged)
    def slowMo(self) -> int:
        return self._slow_mo

    @slowMo.setter
    def slowMo(self, value: int) -> None:
        if self._slow_mo != value:
            self._slow_mo = value
            self.slowMoChanged.emit()

    # ------------------------------------------------------------------
    # Run state
    # ------------------------------------------------------------------

    @pyqtProperty(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @pyqtProperty(bool, notify=stoppingChanged)
    def stopping(self) -> bool:
        return self._stopping

    @pyqtProperty(str, notify=statusTextChanged)
    def statusText(self) -> str:
        return self._status_text

    @pyqtProperty(str, notify=statusKindChanged)
    def statusKind(self) -> str:
        return self._status_kind

    @pyqtProperty(int, notify=progressChanged)
    def progressCurrent(self) -> int:
        return self._progress_current

    @pyqtProperty(int, notify=progressChanged)
    def progressTotal(self) -> int:
        return self._progress_total

    @pyqtProperty(str, notify=logTextChanged)
    def logText(self) -> str:
        return self._log_text

    # ------------------------------------------------------------------
    # Constants / read-only data for QML
    # ------------------------------------------------------------------

    @pyqtProperty("QVariantList", constant=True)
    def tipeValues(self) -> list[str]:
        return TIPE_VALUES

    @pyqtProperty("QVariantList", constant=True)
    def beritaValues(self) -> list[str]:
        return BERITA_VALUES

    @pyqtProperty("QVariantList", constant=True)
    def maintainers(self) -> list[str]:
        return APP_MAINTAINERS

    @pyqtProperty("QVariantList", constant=True)
    def donators(self) -> list[str]:
        return APP_DONATORS

    @pyqtProperty(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @pyqtProperty(str, constant=True)
    def dosenInfo(self) -> str:
        return DOSEN_INFO

    @pyqtProperty(str, constant=True)
    def rowNumberInfo(self) -> str:
        return ROW_NUMBER_INFO

    @pyqtProperty(str, constant=True)
    def semesterInfo(self) -> str:
        return SEMESTER_INFO

    # ------------------------------------------------------------------
    # Config file actions
    # ------------------------------------------------------------------

    @pyqtSlot(QUrl)
    def saveConfigTo(self, url: QUrl) -> None:
        path = url.toLocalFile()
        if not path:
            return
        try:
            self._gather_config().save_to_file(path)
            self._log(f"Saved config to {path} (password excluded)")
        except Exception as exc:
            self._log(f"Failed to save config: {exc}")

    @pyqtSlot(QUrl)
    def loadConfigFrom(self, url: QUrl) -> None:
        path = url.toLocalFile()
        if not path:
            return
        try:
            self._apply_config(LogbookConfig.load_from_file(path))
            self._log(f"Loaded config from {path} (re-enter password)")
        except Exception as exc:
            self._log(f"Failed to load config: {exc}")

    @pyqtSlot(QUrl)
    def setCsvPathFromUrl(self, url: QUrl) -> None:
        path = url.toLocalFile()
        if path:
            self.csvPath = path

    # ------------------------------------------------------------------
    # CSV actions
    # ------------------------------------------------------------------

    @pyqtSlot()
    def loadCsv(self) -> None:
        path = self._csv_path.strip()
        if not path:
            self._log("⚠ No CSV file selected.")
            return
        try:
            abs_path = resolve_to_absolute_path(path)
            with open(abs_path, newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.rows.load(rows)
            while self.rows.count < 3:
                self.rows.addRow()
            self._log(f"Loaded {len(rows)} rows from {path}")
        except Exception as exc:
            self._log(f"Failed to load CSV: {exc}")

    @pyqtSlot(QUrl)
    def loadCsvFromUrl(self, url: QUrl) -> None:
        self.setCsvPathFromUrl(url)
        self.loadCsv()

    @pyqtSlot(QUrl)
    def saveCsvTo(self, url: QUrl) -> None:
        path = url.toLocalFile()
        if not path:
            return
        try:
            data = self.rows.to_rows()
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(data)
            self._log(f"Saved {len(data)} rows to {path}")
        except Exception as exc:
            self._log(f"Failed to save CSV: {exc}")

    @pyqtSlot(int, QUrl)
    def setRowFile(self, row: int, url: QUrl) -> None:
        path = url.toLocalFile()
        if path:
            self.rows.setField(row, "file", path)

    # ------------------------------------------------------------------
    # Automation actions
    # ------------------------------------------------------------------

    @pyqtSlot()
    def start(self) -> None:
        if self._running:
            return
        config = self._gather_config()
        if not config.username or not config.password:
            self._log("⚠ Username and password are required.")
            return

        self._worker = _RunWorker(config)
        self._worker.progress.connect(self._on_progress)
        self._worker.log.connect(self._append_log)
        self._worker.done.connect(self._on_done)

        self._set_running(True)
        self._clear_log()
        self._log(f"Starting automation with {config.csv_path}...")
        self._worker.start()

    @pyqtSlot()
    def stop(self) -> None:
        if self._worker is None or not self._worker.isRunning():
            return
        self._worker.automator.stop()
        self._stopping = True
        self.stoppingChanged.emit()
        self._set_status("Stopping...", "running")

    @pyqtSlot()
    def shutdown(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.automator.stop()
            self._worker.wait(3000)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _gather_config(self) -> LogbookConfig:
        return LogbookConfig(
            username=self._username.strip(),
            password=self._password.strip(),
            dosen=self._dosen.strip(),
            row_number=self._row_number.strip(),
            semester=self._semester.strip(),
            csv_path=self._csv_path.strip(),
            headless=self._headless,
            slow_mo=self._slow_mo,
        )

    def _apply_config(self, config: LogbookConfig) -> None:
        self.username = config.username
        self.password = config.password  # blank: never stored on disk
        self.dosen = config.dosen
        self.rowNumber = config.row_number
        self.semester = config.semester
        self.csvPath = config.csv_path
        self.headless = config.headless
        self.slowMo = config.slow_mo
        self.configLoaded.emit()

    def _set_running(self, running: bool) -> None:
        self._running = running
        self._stopping = False
        self.runningChanged.emit()
        self.stoppingChanged.emit()
        if running:
            self._set_status("Running...", "running")
        else:
            self._set_status("Ready", "idle")

    def _set_status(self, text: str, kind: str) -> None:
        if self._status_text != text:
            self._status_text = text
            self.statusTextChanged.emit()
        if self._status_kind != kind:
            self._status_kind = kind
            self.statusKindChanged.emit()

    def _on_progress(self, current: int, total: int, message: str) -> None:
        self._progress_current = current
        self._progress_total = total
        self.progressChanged.emit()
        self._log(message)

    def _on_done(self, success: bool) -> None:
        self._set_running(False)
        if success:
            self._progress_current = self._progress_total or 1
            self._progress_total = self._progress_total or 1
            self._set_status("Completed ✓", "success")
        else:
            self._set_status("Failed ✗", "error")
        self.progressChanged.emit()
        self._worker = None

    def _clear_log(self) -> None:
        self._log_text = ""
        self.logTextChanged.emit()

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self._append_log(f"[{stamp}] {message}")

    def _append_log(self, message: str) -> None:
        self._log_text = f"{self._log_text}{message}\n" if self._log_text else f"{message}\n"
        self.logTextChanged.emit()
