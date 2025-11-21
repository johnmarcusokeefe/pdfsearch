# controller.py
# mac: source pdfsearch/bin/activate
# windows: venv\Scripts\activate.bat

import sys, os, mimetypes, img2pdf, io, warnings
from PIL import ImageEnhance, Image
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
from pypdf import *
import Levenshtein as levenshtein
import ocrmypdf
from datetime import datetime
from pdf2image import convert_from_path
from pdf2docx import Converter
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject
# my files
from view import MainWindow, FeedbackWindow

from fileview import FileDialogue
#
# Subclass QMainWindow to customize your application's main window
#
class MainController(QObject):
    
    def __init__(self, view, fileview):
        super().__init__()
        # create an instance of the view
        self._view = view
        self._fileview = fileview 
        self.file_path = ""
        self.file_list = []
        # connect signals and slots
        self.connect_signals()
       
    def connect_signals(self):
        #tab1
        self._view.search_open_file_button.clicked.connect(self.call_selected_tab)
        self._view.search_pdf_button.clicked.connect(self.search_pdf)
        self._view.ocr_pdf_button.clicked.connect(self.ocr_file)
        # tab2
        self._view.extract_pages_file_open_button.clicked.connect(self.call_selected_tab)
        self._view.split_pdf_save_file_button.clicked.connect(self.extract_pages)
        # tab3
        self._view.join_pdf_select_multiple_files.clicked.connect(self.set_multiple_file_paths)
    #
    # open file path and add the path to an instance string
    # 
    def set_file_path(self):
        #
        file_path = self._fileview.open_file_dialog()
        if file_path:
            self.file_path = file_path
        # update feedback labels
        print("open file path",self.file_path)
   
   
    # use a feedback window to confirm files added
    def set_multiple_file_paths(self):

        file_list_in = []
        files = self._fileview.open_multiple_files_dialog()
        if len(files) > 1:
            #self.status_bar_label.setText(f"files selected")    
            #print("Selected files:")
            self._view.join_pdf_save_file_button.setEnabled(True)
            for path in files:
                file_list_in.append(path)
            #
            # file dialog box that displays selected file paths for feedback
            #
            self.dialog = FeedbackWindow(file_list_in) # Pass self as parent for WindowModal
            if self.dialog.exec() == 1: # Shows the dialog modally
                self._view.terminal_log.append(f"multiple files selected")
                i = 1
                for file in file_list_in:
                    self._view.file_list_display.addItem(f"{i}: {os.path.basename(file)}")
                    i = i + 1
                # tab 3 join pdf    
                self._view.join_pdf_select_multiple_files.setText(f"File Selected Count: {len(file_list_in)}")
                # set file list values
                self.file_list = file_list_in
            else:
                self._view.terminal_log.append("File Operation Cancelled")
        else:
            self._view.status_bar_label.setText("files not selected")
        
    #
    # process based on selected tab
    #
    def call_selected_tab(self):
        
        print("button validation", self._view.tab_widget.currentIndex())
       
        if self._view.tab_widget.currentIndex() == 0:
            self.set_file_path()
            is_searchable = self.check_pdf()
            print("search tab")
            if is_searchable > 0:
                self._view.search_pdf_button.setEnabled(True)
                self._view.search_pdf_combo.setEnabled(True)
            else:
                self._view.ocr_pdf_button.setEnabled(True)
                self._view.search_pdf_button.setEnabled(False)
                self._view.search_pdf_combo.setEnabled(False)
            #
            self._view.update_labels("search", self.file_path)
        # tab 2 selected
        if self._view.tab_widget.currentIndex() == 1:
            self.set_file_path()
            self.add_pages_to_list_view()
            print("tab 2")
        if self._view.tab_widget.currentIndex() == 2:
            print("tab 3")
        if self._view.tab_widget.currentIndex() == 3:
            print("tab 4")
        if self._view.tab_widget.currentIndex() == 4:
            print("tab 5")
    #
    def add_pages_to_list_view(self):
        self._view.split_pdf_save_file_button.setEnabled(True)
        page_count = self.check_pdf()
        print("extract pages", page_count)
        # loads list of files
        if page_count > 0:
            for page in range(page_count):
                self._view.select_page_list.addItem(str(page))
            self._view.select_page_list.setEnabled(True)
        else:
            self.status_bar_label.setText("file selection requires more than one page")
            self.split_pdf_save_file_button.setEnabled(False)
    #
    def extract_pages(self):
        page_list = []
        #print(f"Selected Pages: {self.page_number_input.selectedIndexes()}")
        selection_model = self._view.select_page_list.selectionModel()
        # Get the selected indexes
        selected_indexes = selection_model.selectedIndexes()
    
        for index in selected_indexes:
            print("index appended ", index.row())
            page_list.append(index.row())
            print(f"Row: {index.row()}, Column: {index.column()}, Data: {index.data()}")
        # call extract and set output path
        self._view.output_file_label.setText(f"output path: {os.path.dirname(self.extract_pdfs(page_list))}")    
    #
    #
    def search_pdf(self):

        found_list = self.process_pdf_file_for_search(self.file_path, self._view.get_search_word(), self._view.get_level())
        if len(found_list) == 0:
            self._view.terminal_log.append("search result empty")
        self._view.search_save_pdf_label.setText(f"{len(found_list)} pages ready to merge")
    #   
    #
    # returns number of text searchable pages
    #
    def check_pdf(self):   
        # You can now open and process the file content
        reader = PdfReader(self.file_path)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            # search text on page and if text found create an array of page numbers
            if text == "":
                return 0
            else:
                #self.page_count_label.setText(f"Page count: {num_pages}")
                return num_pages

    #       
    # subfunction of pdf_search. searches one string
    #
    def fuzzy_word_comparison(self, text, search_word, level):
        l_ratio = 0
        for word in text.split():
            l_ratio = levenshtein.ratio(search_word.lower(), word.lower())
            #print(type(l_ratio))
            if l_ratio > float(level):
                prt_string = f"word matched: {word}"
                self._view.terminal_log.append(prt_string)
                #print(f"word in: {search_word.lower()} | word found: {word.lower()} | lev ratio: {round(float(l_ratio), 2)}")
                return l_ratio
    #
    # search through each page and carry out a fuzzy search logging found works
    # found words and page number are added to an array to allow pages to be 
    # extracted to one file
    #
    def process_pdf_file_for_search(self, file_path, search_word, level):
        self._view.terminal_log.append(f"pdf search path: {file_path} word: {search_word} level: {level}")
        fuzzy_max = 0.0
        fuzzy_total = 0.0
        self._view.status_bar_label.setText("Searching pdf for matches")
        page_list = []
        # in self._view if page list is greater than 0 the save button will be enabled
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        # loop through pages
        self._view.terminal_log.append(f"start of search for: {search_word} at level {level}")
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            # call to check word at a time
            fuzzy_result = self.fuzzy_word_comparison(text, search_word, level)
            if fuzzy_result != None:
                if fuzzy_result > fuzzy_max:
                    fuzzy_max = fuzzy_result
            else:
                fuzzy_result = 0
            if fuzzy_result > 0:
                fuzzy_total = fuzzy_total + fuzzy_result
                page_list.append(page_num)
                self._view.save_pdf_button.setEnabled(True)
            # search text on page and if text found create an array of page numbers
                # if text.lower().find(search_string.get().lower()) != -1:
                #     print("text found on page ", page_num)
        print(f"pdf search page list: {page_list}")
        self._view.search_found_label.setText("No Matches Found")
        if len(page_list) > 0:
            fuzzy_average = round(fuzzy_total/len(page_list), 1)
            search_found_stats = f"Highest match is {str(round(fuzzy_max,2))} and average match is {str(round(fuzzy_average,2))}"
            self._view.search_found_label.setText(search_found_stats)
            self._view.status_bar_label.setText(f"search matched {len(page_list)}")
        else:
            self._view.status_bar_label.setText("no results found")
        return page_list
    #
    # create a text searchable document
    #
    def ocr_file(self):
        """
        Adds an OCR text layer to a scanned PDF, making it searchable.
        """
        output_pdf_path = "output/ocr_"+os.path.basename(self.file_path) 
        self._view.status_bar_label.setText("ocr pdf")
        ocrmypdf.ocr(self.file_path, output_pdf_path, skip_text=True, oversample=300, clean=True)
        print(f"OCR completed. Searchable PDF saved to: {output_pdf_path}")
        # sets the search path
        self.file_path = output_pdf_path
        self._view.open_file_label.setText(self.file_path)
        self._view.search_pdf_button.setEnabled(True)
        self._view.search_pdf_combo.setEnabled(True)
    #
    # extract pages
    #
    def extract_pdfs(self, page_list):
        # Open the original PDF file
        output_dir = os.path.dirname(self.file_path)
        extract_to_dir = "/"+os.path.basename(self.file_path).rsplit('.', 1)[0]
        # Create the directory if it doesn't exist
        if not os.path.exists(output_dir+extract_to_dir):
            os.makedirs(output_dir+extract_to_dir) # os.makedirs creates intermediate directories too
        print("extract", output_dir)
        try:
            reader = PdfReader(self.file_path)
            num_pages = len(page_list) 
            for i in range(num_pages):
                writer = PdfWriter()
                # get the value from the page list
                ind = page_list[i]
                writer.add_page(reader.pages[ind])
                output_pdf_path = f"{output_dir+extract_to_dir}/{ind}.pdf"  # Naming convention for output files
                with open(output_pdf_path, "wb") as output_file:
                    writer.write(output_file)
                print(f"Page {ind} extracted and saved as {output_pdf_path}")
                self._view.terminal_log.append(f"Page {ind} extracted and saved as {output_pdf_path}")
            return output_pdf_path

        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")     
    #
    # merge pdfs
    #
    def merge_pdfs(self, file_name, file_list):
        
        pdf_ext = ".pdf"
        self._view.status_bar_label.setText("merging pdf")
        if pdf_ext.lower() in file_name.lower():
            output_filename = file_name
        else:
            output_filename = file_name+pdf_ext
        print("call merge pdfs")
        """
        Merges a list of PDF files into a single output PDF.

        """
        merger = PdfWriter()
        for path in file_list:
            print("merge pdf path: ",path)
            mime_type = mimetypes.guess_type(path)[0]
            print(mime_type)
            # tests image type and converts
            if(mime_type == "image/png" or mime_type == "image/jpeg" or mime_type == "image/jpg"):
                converted_path = self.image_to_pdf(self, path)
                merger.append(converted_path)
            else:
                merger.append(path)
            #    
            try:
                with open(output_filename, "wb") as output_file:
                    merger.write(output_file)
            except Exception as e:
                print(f"Error saving file: {e}")
        merger.close()
        self._view.terminal_log.append(f"PDFs merged successfully:\n{output_filename}")
        print(f"PDFs merged successfully into {output_filename}")
    #
    # pdf to image converter
    #
    def pdf_to_image(_view, file_path, dpi_in, fmt_in, brightness=0.99):

        # Store Pdf with convert_from_path function
        images = convert_from_path(_view, file_path, dpi=dpi_in, fmt=fmt_in)

        for i in range(len(images)):
            # Save pages as images in the pdf
            enhancer = ImageEnhance.Brightness(images[i])
            adj_image = enhancer.enhance(brightness) # factor > 1 for brighter, < 1 for darker
            adj_image.save('output/images/page'+str(i)+"."+fmt_in)
            _view.terminal_log.append('saved: output/images/page'+str(i)+"."+fmt_in)
        
        print("extracted images", len(images))
        return "output/images", len(images)
    #
    #
    #
    def image_to_pdf(self, img_path):
        pdf_path = img_path+".pdf"
        try:
        # Open the image using Pillow (PIL)
            image = Image.open(img_path)
        # Convert the image to PDF bytes using img2pdf
            bytes_to_merge = img2pdf.convert(image.filename)
        # Write the PDF bytes to a file
            # with open(pdf_path, "wb") as f:
            #     f.write(pdf_bytes)
            # print(f"Successfully converted '{img_path}' to '{pdf_path}'")
        except FileNotFoundError:
            print(f"Error: Image file not found at '{img_path}'")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the image if it was opened successfully
            if 'image' in locals() and image:
                image.close()
            # one page
            return PdfReader(io.BytesIO(bytes_to_merge))
    #
    # convert pdf to word document 
    #
    def convert_pdf_to_word(docx_file_path, file_path):
        print(file_path)
        """
        Converts a PDF file to a DOCX (Word) document.

        Args:
            pdf_file_path (str): The path to the input PDF file.
            docx_file_path (str): The desired path for the output DOCX file.
        """
        try:
            cv = Converter(file_path)
            cv.convert(docx_file_path, start=0, end=None) # start and end pages (optional)
            cv.close()
            print(f"Successfully converted '{file_path}' to '{docx_file_path}'")
        except Exception as e:
            print(f"Error converting PDF to Word: {e}")
    #
    # save pdf from a list of pages
    #
    def save_pdf(self, search_string, page_list):
        # all files saved to output
        self._view.status_bar_label.setText("save pdf")
        now = datetime.now()
        print("save pdf", self.file_path)
        print("page list array", page_list)
        reader = PdfReader(self.file_path)
        if len(page_list) > 0:
            writer = PdfWriter()
            for page in page_list:
                writer.add_page(reader.pages[page])
            try:
                out_path = f"output/{search_string}_{int(now.timestamp())}.pdf"
                with open(out_path, "wb") as output_pdf:
                    writer.write(output_pdf)
                self._view.terminal_log.append(f"extracted pdf pages saved: {out_path}")
                self._view.output_file_label.setText(f"Output Path: {out_path}")
            except Exception as e:
                self._view.terminal_log.append(f"Error saving file: {e}")
        else:
            self._view.terminal_log.append("no files in list save_pdf")
            
        self._view.save_pdf_button.setEnabled(False)
    #
    #
    #
    # def check_if_ocr_required(self, is_text_plus_num_pages):
    #     if is_text_plus_num_pages == 0:
    #         self.ocr_file(self._view, self._view.file_path)
    #         self._view.search_pdf_button.setEnabled(True)  
    #     else:
    #         self.page_number_input.setEnabled(True)
    #         self._view.search_pdf_button.setEnabled(True)
    #         self._view.terminal_log(f"File page count: {is_text_plus_num_pages}")
    #         self._view.page_number_input.clear()
    #         pages = self.check_pdf(self._view.file_path)
    #         self._view.page_count_label.setText(f"Page count: {pages}")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    view = MainWindow()
    fileview = FileDialogue()
    controller = MainController(view, fileview)
    
    view.show()
    sys.exit(app.exec())