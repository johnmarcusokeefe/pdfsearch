# controller.py
from PySide6.QtWidgets import QApplication, QFileDialog
from model import DocumentModel
from view import MainWindow, FeedbackWindow
import sys

class MainController:
    def __init__(self):
        self.model = DocumentModel()
        self.view = MainWindow()

        # connect view signals
        self.view.select_files.connect(self.handle_select_files)
        self.view.scan_files.connect(self.handle_scan)
        self.view.ocr_files.connect(self.handle_ocr)

    def handle_select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            None, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        if files:
            self.model.set_files(None, files)
            dialog = FeedbackWindow(files)
            if dialog.exec():
                self.view.label.setText(f"{len(files)} file(s) selected.")

    def handle_scan(self):
        for f in self.model.file_list:
            page_count = self.model.count_pdf_pages(f)
            print(f"{f}: {page_count} pages")

    def handle_ocr(self):
        for f in self.model.file_list:
            if not self.model.is_text_searchable(f):
                print(f"Running OCR on {f}")
                self.model.run_ocr(f)
            else:
                print(f"{f} already searchable.")

    def run(self):
        self.view.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MainController()
    controller.run()
    sys.exit(app.exec())
