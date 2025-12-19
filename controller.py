# controller.py
# mac: source pdfsearch/bin/activate
# windows: .venv\Scripts\activate.bat

import sys, os, mimetypes, img2pdf, warnings, re, asyncio
# import pypdfium2 as pdfium
import pytesseract


from PIL import ImageEnhance, Image
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
import Levenshtein as levenshtein
from datetime import datetime
from pdf2image import convert_from_path
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
import threading
#gui
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
# local files
from view import MainWindow, FeedbackWindow
from fileview import FileDialogue
from fileprocess import ExtractText
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
        self.page_list = []
        # connect signals and slots
        self.connect_signals()
    #
    # connect view signals
    #     
    def connect_signals(self):
        #tab1
        self._view.search_open_file_button.clicked.connect(self.call_selected_tab)
        self._view.ocr_pdf_button.clicked.connect(self.extract_text_pdfium)
        self._view.search_pdf_button.clicked.connect(self.search_pdf)
        self._view.save_pdf_button.clicked.connect(self.save_pdf_from_search)
        # tab2
        self._view.extract_pages_file_open_button.clicked.connect(self.call_selected_tab)
        self._view.split_pdf_save_file_button.clicked.connect(self.extract_pages)
        # tab3
        self._view.join_pdf_select_multiple_files.clicked.connect(self.call_selected_tab)
        self._view.join_pdf_save_file_button.clicked.connect(self.merge_pdfs)
        self._view.join_images_save_file_button.clicked.connect(self.merge_images_to_pdf)
        # tab4
        self._view.extract_images_from_pdf_open_file_button.clicked.connect(self.call_selected_tab)
        #
        self._view.extract_images_from_pdf_filetype_combo.currentIndexChanged.connect(self.extract_images_from_pdf_button_check)
        self._view.extract_images_from_pdf_quality_combo.currentIndexChanged.connect(self.extract_images_from_pdf_button_check)
        self._view.extract_images_from_pdf_run_button.clicked.connect(self.pdf_to_image)
        # tab5
        self._view.extract_pdf_open_file_button.clicked.connect(self.call_selected_tab)
        self._view.extract_pdf_to_word_content_button.clicked.connect(self.convert_pdf_to_word)
        self._view.extract_pdf_to_text_button.clicked.connect(self.convert_pdf_to_text)

        self._view.tab_widget.currentChanged.connect(self.tab_change)

    # ------------------- #
    #  reset all values    #
    # --------------------#
    

    def tab_change(self):
        print("new tab selected",self._view.tab_widget.currentIndex()+1)
        self.file_path = ""
        self.file_list = []
        self._view.search_found_label.setText("Search Pending")
        self._view.search_save_pdf_label.setText("0 pages ready to merge")
        self._view.output_file_label.setText("Output path:")
        self.set_status_bar("")
        self._view.join_pdf_select_multiple_files.setText("Select Files")
        self._view.select_page_list.clear()
        self._view.extract_images_from_pdf_filetype_combo.setCurrentIndex(0)
        self._view.extract_images_from_pdf_quality_combo.setCurrentIndex(0)
        self._view.extract_images_from_pdf_run_button.setEnabled(False)
        self._view.file_list_display.clear()
        print("file variables", self.file_path, self.file_list)
    #
    # process based on selected tab
    #
    def call_selected_tab(self):
        
        tab_number = self._view.tab_widget.currentIndex()
        print("call_selected_tab method", tab_number + 1)
        is_text = False
        if tab_number == 0:
            self.set_file_path()
            self._view.search_open_file_label.setText(f"filepath: {self.file_path}")
            page_count = self.check_pdf()
            
           
            # extracts text every 
            print(self.page_list)
            if is_text > 0:
                self._view.search_pdf_button.setEnabled(True)
                self._view.search_pdf_combo.setEnabled(True)
                self.set_status_bar(f"{len(self.page_list)} pages ready for search")
            else:
                self._view.ocr_pdf_button.setEnabled(True)
                self._view.search_pdf_button.setEnabled(False)
                self._view.ocr_pdf_button.setText(f"{page_count} pages ready to OCR")
                self._view.search_pdf_combo.setEnabled(False)
                self.set_status_bar("file ready for ocr")


        # tab 2 selected
        if tab_number == 1:
            self.set_file_path()
            self.add_pages_to_list_view()
            print("tab 2")

        # tab 3
        if tab_number == 2:
            print("tab 3")
            self.set_multiple_file_paths()
            # check mime type to enable buttons
            if len(self.file_list) > 0:
                mime_type = mimetypes.guess_type(self.file_list[0])[0]
                print(mime_type)
                # # tests image type and converts
                if mime_type  == "image/jpeg" :
                    self._view.join_images_save_file_button.setEnabled(True)
                    self._view.join_pdf_save_file_button.setEnabled(False)
                if mime_type == "application/pdf":
                    self._view.join_pdf_save_file_button.setEnabled(True)
                    self._view.join_images_save_file_button.setEnabled(False)
            else:
                self.set_status_bar("no files selected")
                self.file_list = []
                self._view.select_page_list.clear()

        # tab 4
        if tab_number == 3:
            self.set_file_path()
            if self.file_path:
                self._view.extract_images_from_pdf_label.setText(f"Path: {self.file_path}")
                self._view.extract_images_from_pdf_filetype_combo.setEnabled(True)
                self._view.extract_images_from_pdf_quality_combo.setEnabled(True)
        # tab 5
        if tab_number == 4:
            print("tab 5")
            self.set_file_path()
            self._view.extract_pdf_content_label.setText(f"Extract PDF Filepath: {self.file_path}")
            # test if text
            num_pages = self.check_pdf()
            self.set_status_bar(f"{num_pages} pages found with text")
            if num_pages == 0:
                self.ocr_pdf_file() 
                self._view.extract_pdf_to_text_button.setEnabled(True)
                self._view.extract_pdf_to_word_content_button.setEnabled(True)
            else:
                self._view.extract_pdf_to_text_button.setEnabled(True)
                self._view.extract_pdf_to_word_content_button.setEnabled(True)
    #
    # open file path and add the path to an instance string
    # 
    def set_file_path(self):
        #
        file_path = self._fileview.open_file_dialog()
        if file_path:
            
            self.file_path = file_path
            self.set_status_bar("file path set")
            self.set_log(f"file path {self.file_path} set")
        else:
            print("no file path set")
    #
    #
    #
    def set_multiple_file_paths(self):
        file_list_in = []
        files = self._fileview.open_multiple_files_dialog()
        if len(files) > 0:
            self.set_status_bar("multiple file paths set")    
            self._view.join_pdf_save_file_button.setEnabled(True)
            for path in files:
                file_list_in.append(path)
            #
            # file dialog box that displays selected file paths for feedback
            #
            self.dialog = FeedbackWindow(file_list_in) # Pass self as parent for WindowModal
            if self.dialog.exec() == 1: # Shows the dialog modally
                self.set_log(f"multiple files selected")
                self._view.file_list_display.clear()
                i = 1
                for file in file_list_in:
                    self._view.file_list_display.addItem(f"{i}: {os.path.basename(file)}")
                    i = i + 1
                # tab 3 join pdf    
                self._view.join_pdf_select_multiple_files.setText(f"File Selected Count: {len(file_list_in)}")
                # set file list values
                self.file_list = file_list_in
            else:
                self.set_log("File Operation Cancelled")
        else:
            self.set_status_bar("files not selected")
    #   
    # add page numbers to a file list view
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
            self.set_status_bar("pages selected")
        else:
            self.set_status_bar("file selection requires more than one page")
            self._view.split_pdf_save_file_button.setEnabled(False)
    #
    #
    #
    def extract_pages(self):
        page_list = []
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
    # main search method that gets input values,
    #
    def search_pdf(self):
        # get the input word from the input widget
        search_word = self._view.search_pdf_input_word.text()
        # get an interger value to set levenshtein level
        level = self._view.search_pdf_combo.currentText()
        self.file_list = self.process_pdf_file_for_search(search_word, level)
        print(self.file_list)
        if len(self.file_list) == 0:
            self.set_log("search result empty")
        self._view.search_save_pdf_label.setText(f"{len(self.file_list)} pages ready to merge")
    #   
    # returns number of text searchable pages or false if requires ocr
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
    def extract_text_from_image(self, file_path_in):
        # use opencv for port processing
        # Open an image using Pillow
        try:
            img = Image.open(file_path_in)
            # Use image_to_string to extract text
            text = pytesseract.image_to_string(img)
            print(text)
        except ImportError as e:
            print(f"Error importing modules: {e}")
        except FileNotFoundError as e:
            print(f"Tesseract executable not found. Check your PATH or specify tesseract_cmd. Error: {e}")
        
    #       
    # subfunction of pdf_search. searches one page of text.
    #
    def fuzzy_word_comparison(self, text, search_word, level):
        found_list = []
        l_ratio = 0
        i = 0
        for word in text.split():
            l_ratio = levenshtein.ratio(search_word.lower(), word.lower())
            # only adds if greater match found
            if l_ratio > float(level):
                i = i + 1
                self.set_log(f"text word: {word} search word: {search_word} ratio: {l_ratio} count: {i}")
                found_list.append(f"word found: {word} ratio: {l_ratio}")

        print(found_list)
        return l_ratio, i

    #
    # search through each page and carry out a fuzzy search logging found works
    # found words and page number are added to an array to allow pages to be 
    # extracted to one file
    #
    def process_pdf_file_for_search(self, search_word, level):
        found_page_list = []
        self.set_log(f"pdf search path: {self.file_path} word: {search_word} level: {level}")
        fuzzy_max = 0.0
        fuzzy_total = 0.0
        self.set_status_bar("Searching pdf for matches")
        page_list = []
        # in self._view if page list is greater than 0 the save button will be enabled
        num_pages = len(self.page_list)
        # loop through pages
        self.set_log(f"start of search for: {search_word} at level {level}")
        for page_num in range(num_pages):
            text = self.page_list[page_num]
            # call to check word at a time
            fuzzy_result, found_count = self.fuzzy_word_comparison(text, search_word, level)
            if fuzzy_result != None:
                if fuzzy_result > fuzzy_max:
                    fuzzy_max = fuzzy_result
            else:
                fuzzy_result = 0
            #
            if found_count > 0:
                fuzzy_total = fuzzy_total + fuzzy_result
                found_page_list.append(page_num)
                self._view.save_pdf_button.setEnabled(True)
                self.set_status_bar(f"total matches {found_count}")
        
        print(f"pdf search page list: {found_page_list}")
        # stats
        if len(found_page_list) > 0:
            fuzzy_average = fuzzy_total/len(found_page_list)
            search_found_stats = f"Highest match is {str(round(fuzzy_max,2))} and average match is {str(round(fuzzy_average,2))}"
            self.set_log(search_found_stats)
            self.set_status_bar(f"search matched {len(self.page_list)}")
        else:
            self.set_status_bar("no results found")
        #
        return found_page_list
    #
    # create a text searchable document
    #
    #def run_ocr(self, output_pdf_path, skip_text, oversample, clean):

    #    ocrmypdf.ocr(self.file_path, output_pdf_path, skip_text=skip_text, oversample=oversample, clean=clean)
    #
    #
    #
    def extract_text_pdfium(self):
        
        #page_array = []
        # if self.file_path:

        #     pdf = pdfium.PdfDocument(self.file_path)
        #     for i, page in enumerate(pdf):
        #         img = page.render(scale=300/72).to_pil()
        #         text = pytesseract.image_to_string(img)
        #         # print(f"--- Start Page {i+1} ---")
        #         # print(text)
        #         page_array.append(text)
        et = ExtractText()
        
        thread = threading.Thread(target=et.extract_text, args=(self.file_path, self.page_list, self))
        thread.start()
       
        #print(page_array)
        #self.thread.join()

        #return page_array 
#
    
    def ocr_pdf_file(self):
        self._view.ocr_pdf_label.setText("Running OCR of file")
        """
        Adds an OCR text layer to a scanned PDF, making it searchable.
        """
        output_pdf_path = "output/ocr_"+os.path.basename(self.file_path) 
        #ocrmypdf.ocr(self.file_path, output_pdf_path, skip_text=skip_text, oversample=oversample, clean=clean)
        asyncio.run(self.run_ocr(output_pdf_path, True, 300, True))
        print(f"OCR completed. Searchable PDF saved to: {output_pdf_path}")
        # sets the search path
        self.file_path = output_pdf_path
        self._view.search_open_file_label.setText(self.file_path)
        #set buttons true
        self._view.search_pdf_button.setEnabled(True)
        self._view.search_pdf_combo.setEnabled(True)
        self._view.ocr_pdf_label.setText("ocr complete")
        self.set_status_bar("searchable file available")
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
                self.set_log(f"Page {ind} extracted and saved as {output_pdf_path}")
            return output_pdf_path

        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")     
    #
    # merge pdfs
    #
    def merge_pdfs(self):
        pdf_ext = ".pdf"
        file_list = self.file_list
        flag = self._view.auto_filename.isChecked()
        self.set_status_bar("merging pdf files")
        # filename needs to be created for merged files
        if flag == 0:
            file_name = self._fileview.user_filename_input_dialog()
        else:
            ts = datetime.now().timestamp()
            file_name = "output/merge_pdf_"+str(ts)+".pdf"
        #
        if len(file_list) > 0:
            # test if has pdf extension
            if pdf_ext.lower() in file_name.lower():
                output_filename = file_name
            else:
                output_filename = file_name+pdf_ext
            print("call merge pdfs")
            """
            Merges a list of PDF files into a single output PDF.
            """
            merger = PdfWriter()
            try:
                for pdf in file_list:
                    with open(pdf, 'rb') as pdf_file:
                        merger.append(pdf_file) 
                    with open(output_filename, 'wb') as output_file:
                        merger.write(output_file)
                merger.close() 
            except Exception as e:
                print(f"Error saving file: {e}")
            self.set_log(f"PDFs merged successfully:\n{output_filename}")
            print(f"PDFs merged successfully into {output_filename}")
        else:
            self.set_status_bar("no file name or path supplied")
    #
    # check if image conversion buttons are selected
    #
    def extract_images_from_pdf_button_check(self):
        print("combo change")
        if self._view.extract_images_from_pdf_filetype_combo.currentIndex() > 0 and self._view.extract_images_from_pdf_quality_combo.currentIndex() > 0:
            self._view.extract_images_from_pdf_run_button.setEnabled(True)
        else:
            self._view.extract_images_from_pdf_run_button.setEnabled(False)
        if self.file_path == "":
            self._view.extract_images_from_pdf_run_button.setEnabled(False)
    #
    # pdf to image converter
    #
    def pdf_to_image(self):
        fmt_in = self._view.extract_images_from_pdf_filetype_combo.currentText()
        dpi_in = self._view.extract_images_from_pdf_quality_combo.currentText()
        # pattern returns all digits. example "medium: 300pdi"
        pattern = r'\d+'
        # Search for the pattern in the text
        match = re.search(pattern, dpi_in)
        print("match", match)
        if match:
            dpi_str = match.group()
            # Optionally, convert the matched string to an integer
            dpi_int = int(dpi_str)
            print(f"The first occurrence of an integer as an int: {dpi_int}")
        else:
            print("No integer found in the text.")
            dpi_int = 150
        
        print("args", dpi_in, fmt_in)
        brightness=0.99
        # Store Pdf with convert_from_path function
        print(self.file_path)
        images = convert_from_path(self.file_path, dpi=dpi_int, fmt=fmt_in)
        for i in range(len(images)):
            # Save pages as images in the pdf
            enhancer = ImageEnhance.Brightness(images[i])
            adj_image = enhancer.enhance(brightness) # factor > 1 for brighter, < 1 for darker
            adj_image.save('output/images/page'+str(i)+"."+fmt_in)
            self.set_log('saved: output/images/page_'+str(i)+"."+fmt_in)
        print("extracted images", len(images))
        #return "output/images", len(images)
    #
    #
    #      
    def merge_images_to_pdf(self):

        flag = self._view.auto_filename.isChecked()
        if flag == 0:
            output_path = self._fileview.user_filename_input_dialog()          
        else:
            ts = datetime.now().timestamp()
            output_path = "output/image_to_pdf_"+str(ts)+".pdf"

        if not self.file_list:
            print("No JPEG images found.")
        else:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(self.file_list))
            print(f"Successfully created lossless PDF: {output_path}")
    #
    # convert pdf to word document 
    #
    def convert_pdf_to_word(self):
        """
        Converts a PDF file to a DOCX (Word) document.

        Args:
            pdf_file_path (str): The path to the input PDF file.
            docx_file_path (str): The desired path for the output DOCX file.
        """
        try:
            filename = os.path.basename(self.file_path)+".docx"
            docx_file_path = "output/"+filename
            cv = Converter(self.file_path)
            cv.convert(docx_file_path, start=0, end=None) # start and end pages (optional)
            cv.close()
            print(f"Successfully converted '{self.file_path}' to '{docx_file_path}'")
            self.set_status_bar("word file created")
        except Exception as e:
            print(f"Error converting PDF to Word: {e}")
    #
    # convert pdf to text
    #
    def convert_pdf_to_text(self):
        """Extracts all text from a digital PDF file."""
        reader = PdfReader(self.file_path)
        text = ""
        filename = os.path.basename(self.file_path)
        for page in reader.pages:
            text += page.extract_text() or "" # Use or "" to handle empty pages
        with open("output/"+filename+".txt", 'w') as f:
            f.write(text)
        self.set_status_bar("text file created")
    #
    # save pdf from a list of pages
    #
    def save_pdf_from_search(self):
        # all files saved to output
        page_list = self.file_list
        # get save to folder
        folder_path = self._fileview.open_folder_dialog()
        self.set_log(f"folder selected {folder_path}")
        if folder_path:
            # search specific term used to create output file
            search_string = self._view.search_pdf_input_word.text()
            self.set_status_bar("save pdf")
            now = datetime.now()
            print("save pdf", self.file_path)
            print("page list array", page_list)
            reader = PdfReader(self.file_path)
            if len(page_list) > 0:
                writer = PdfWriter()
                for page in page_list:
                    writer.add_page(reader.pages[page])
                try:
                    out_path = f"{folder_path}/{search_string}_{int(now.timestamp())}.pdf"
                    with open(out_path, "wb") as output_pdf:
                        writer.write(output_pdf)
                    self.set_log(f"extracted pdf pages saved: {out_path}")
                    self._view.output_file_label.setText(f"Output Path: {out_path}")
                except Exception as e:
                    self.set_log(f"Error saving file: {e}")
            else:
                self.set_log("no files in list save_pdf")
        else:
            self.set_status_bar("no folder selected")
                
        self._view.save_pdf_button.setEnabled(False)
    #
    # set status bar message
    #
    def set_status_bar(self, message):
        self._view.status_bar_label.setText(message)

    def set_log(self, message):
        self._view.terminal_log.append(message) 

if __name__ == "__main__":

    app = QApplication(sys.argv)

    view = MainWindow()
    fileview = FileDialogue()
    controller = MainController(view, fileview)
    
    
    
    view.show()
    sys.exit(app.exec())