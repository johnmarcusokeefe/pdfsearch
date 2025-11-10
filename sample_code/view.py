# view.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog, QDialog
)
from PySide6.QtCore import Signal

class FeedbackWindow(QDialog):
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Feedback Window")
        layout = QVBoxLayout(self)

        label = QLabel("Files Selected:")
        self.list_widget = QListWidget()
        for f in file_list:
            self.list_widget.addItem(f)

        self.btn_add = QPushButton("Add Files")
        self.btn_cancel = QPushButton("Cancel")

        layout.addWidget(label)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_cancel)

        self.btn_add.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)


class MainWindow(QMainWindow):
    select_files = Signal()
    scan_files = Signal()
    ocr_files = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scan and Search")

        central = QWidget()
        layout = QVBoxLayout(central)

        self.label = QLabel("No files selected.")
        self.btn_select = QPushButton("Select Files")
        self.btn_scan = QPushButton("Scan")
        self.btn_ocr = QPushButton("Run OCR")

        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_scan)
        layout.addWidget(self.btn_ocr)

        self.setCentralWidget(central)
        self._connect_signals()

    def _connect_signals(self):
        self.btn_select.clicked.connect(self.select_files)
        self.btn_scan.clicked.connect(self.scan_files)
        self.btn_ocr.clicked.connect(self.ocr_files)
