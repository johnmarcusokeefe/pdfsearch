# model.py
import os
from pypdf import PdfReader
import ocrmypdf
from pdf2image import convert_from_path

class DocumentModel:
    def __init__(self):
        self.file_path = None
        self.file_list = []

    def set_files(self, path, files):
        self.file_path = path
        self.file_list = files

    def count_pdf_pages(self, file_path):
        try:
            return len(PdfReader(file_path).pages)
        except Exception as e:
            print(f"Error counting pages: {e}")
            return 0

    def is_text_searchable(self, file_path):
        """Return True if PDF has extractable text."""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                if page.extract_text():
                    return True
            return False
        except Exception:
            return False
