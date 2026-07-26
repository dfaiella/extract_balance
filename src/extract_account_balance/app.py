import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui

from .chart import BalanceChartCanvas
from .pdf_tools import extract_description_from_text, extract_rows_from_text, read_pdf_text
from .storage import append_activity_log, copy_imported_pdf, get_activity_log_path, get_backup_dir, get_history_path, load_statement_history, save_statement_history, upsert_statement


def sort_records_by_date(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(rows, key=lambda row: str(row.get("date", "")), reverse=True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Account Balance Viewer")
        self.resize(800, 500)
        self.records: List[Dict[str, float | str]] = []
        self.history: List[Dict[str, Any]] = []
        self.current_period_index = -1
        self.history_path = get_history_path()

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        self.setAcceptDrops(True)
        central.setAcceptDrops(True)
        self._install_drop_handlers(self)
        self._install_drop_handlers(central)

        top_row = QtWidgets.QHBoxLayout()
        self.load_button = QtWidgets.QPushButton("Load PDF\n(or Drag/Drop anywhere)")
        self.load_button.setMinimumHeight(40)
        self.load_button.clicked.connect(self.choose_file)
        top_row.addWidget(self.load_button)
        layout.addLayout(top_row)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Date", "Balance"])
        layout.addWidget(self.table)

        self.chart_view = BalanceChartCanvas(self)
        layout.addWidget(self.chart_view)

        nav_row = QtWidgets.QHBoxLayout()
        self.prev_button = QtWidgets.QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_period)
        nav_row.addWidget(self.prev_button)

        self.next_button = QtWidgets.QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_period)
        nav_row.addWidget(self.next_button)
        layout.addLayout(nav_row)

        self.status = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status)

        self._create_menu_bar()
        self.load_history()

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        data_menu = menu_bar.addMenu("Data")

        open_data_action = QtGui.QAction("Open Data Folder", self)
        open_data_action.triggered.connect(self.open_data_folder)
        data_menu.addAction(open_data_action)

        view_transactions_action = QtGui.QAction("View Transactions", self)
        view_transactions_action.triggered.connect(self.view_transactions)
        data_menu.addAction(view_transactions_action)

        view_log_action = QtGui.QAction("View Log", self)
        view_log_action.triggered.connect(self.view_log)
        data_menu.addAction(view_log_action)

    def load_history(self) -> None:
        try:
            self.history = load_statement_history(self.history_path)
        except Exception as exc:
            self._show_error(
                "Could not load saved transactions",
                f"The transaction history file could not be read.\n\n{exc}\n\nTry reopening the app or restoring the file from the backup folder.",
            )
            self.history = []

        if self.history:
            self.current_period_index = len(self.history) - 1
            self.show_period(self.current_period_index)
        else:
            self.records = []
            self._render_table(self.records)
            self._render_chart(self.records)
            self.status.showMessage("No saved statements yet")

    def choose_file(self) -> None:
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if file_name:
            self.process_file(file_name)

    def open_data_folder(self) -> None:
        try:
            self._open_path(self.history_path.parent)
        except Exception as exc:
            self._show_error("Could not open data folder", str(exc))

    def view_transactions(self) -> None:
        try:
            self._open_path(self.history_path)
        except Exception as exc:
            self._show_error("Could not open transactions file", str(exc))

    def view_log(self) -> None:
        try:
            self._open_path(get_activity_log_path())
        except Exception as exc:
            self._show_error("Could not open log file", str(exc))

    def _open_path(self, path: Path) -> None:
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(path)))

    def process_file(self, file_name: str) -> None:
        path = Path(file_name)
        if not path.exists():
            self._show_error(
                "Selected file does not exist",
                "The PDF could not be found. Re-select the file or make sure it has not been moved or renamed.",
            )
            return

        try:
            text = read_pdf_text(path)
            rows = extract_rows_from_text(text)
            description = extract_description_from_text(text) or path.stem
        except Exception as exc:
            self._show_error(
                "Could not read PDF",
                f"The PDF could not be parsed.\n\n{exc}\n\nTry using a different PDF, checking that the file is not corrupted, or installing the offline PDF reader dependencies.",
            )
            return

        if not rows:
            self._show_error(
                "No transaction rows were found",
                "The PDF text was read, but no rows could be extracted. Try a different statement or adjust the parser for this format.",
            )
            return

        try:
            imported_copy = copy_imported_pdf(path)
            self.history = upsert_statement(self.history, path.name, description, [
                {"date": row["date"], "balance": row["balance"], "filename": path.name, "description": description}
                for row in rows
            ])
            self.current_period_index = len(self.history) - 1
            self._persist_history()
            append_activity_log(f"Imported PDF: {path.name}", get_activity_log_path())
            self.status.showMessage(f"Imported {path.name} and saved a copy to {imported_copy}")
            self.show_period(self.current_period_index)
        except Exception as exc:
            self._show_error(
                "Could not save imported statement",
                f"The transaction data could not be saved.\n\n{exc}\n\nCheck that the data folder is writable and that the history file has not been locked by another process.",
            )

    def show_period(self, index: int) -> None:
        if not 0 <= index < len(self.history):
            return
        entry = self.history[index]
        self.records = sort_records_by_date(entry.get("records", []))
        self._render_table(self.records)
        self._render_chart(self.records)
        self.status.showMessage(f"{entry.get('description', entry.get('filename', 'Unknown'))} ({len(self.records)} rows)")
        self.current_period_index = index

    def show_previous_period(self) -> None:
        if self.current_period_index > 0:
            self.show_period(self.current_period_index - 1)

    def show_next_period(self) -> None:
        if self.current_period_index < len(self.history) - 1:
            self.show_period(self.current_period_index + 1)

    def _persist_history(self) -> None:
        try:
            save_statement_history(self.history, self.history_path)
        except Exception as exc:
            self._show_error(
                "Could not persist transaction history",
                f"The history file could not be updated.\n\n{exc}\n\nCheck the data folder permissions or restore the backup copy from the backups folder.",
            )

    def _show_error(self, title: str, message: str) -> None:
        self.status.showMessage(title)
        QtWidgets.QMessageBox.critical(self, title, message)

    def _render_table(self, rows: List[Dict[str, float | str]]) -> None:
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(row["date"])))
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(f"{float(row['balance']):.2f}"))

    def _render_chart(self, rows: List[Dict[str, float | str]]) -> None:
        self.chart_view.render_records(rows)

    def _install_drop_handlers(self, widget: QtWidgets.QWidget) -> None:
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = self._handle_drag_enter
        widget.dropEvent = self._handle_drop
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setAcceptDrops(True)
            child.dragEnterEvent = self._handle_drag_enter
            child.dropEvent = self._handle_drop

    def _handle_drag_enter(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _handle_drop(self, event: QtGui.QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if local_path:
                self.process_file(local_path)
                event.acceptProposedAction()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
