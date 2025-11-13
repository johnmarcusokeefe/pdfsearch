from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os, time, subprocess
import controller

class FeedbackWindow(QDialog):
    def __init__(self, file_list, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Feedback Window")
        list_widget = QListWidget()
        layout = QVBoxLayout()

        label = QLabel("Files Selected.")
        i = 0
        
        for line in file_list:
            list_widget.addItem(str(os.path.basename(line)))
            i = i + 1

        layout.addWidget(list_widget)

        accept_button = QPushButton("Add Files")
        accept_button.clicked.connect(self.accept) # Connect to accept or reject to close the dialog
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(accept_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)
        
class MainWindow(QMainWindow):

    def __init__(self, file_path, pages=[], file_list=[]):
        super().__init__(file_path)
       
        self.setWindowTitle("Scan and Search")
        self.file_path = file_path
        self.pages = pages
        self.file_list = file_list

        self.custom_file_name = ""

        self.ctr = controller.MainController(self.file_path, file_list=[])
    
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.setGeometry(200, 200, 800, 400)
        self.status_bar = self.statusBar()
        
        self.status_bar_label = QLabel()
        self.status_bar_label.setMinimumWidth(800)
        self.status_bar_label.setAlignment(Qt.AlignCenter)
        self.status_bar.addPermanentWidget(self.status_bar_label)

        self.file_name = ""
        self.current_directory = ""
        self.page_count = ""
        self.file_size = ""
        self.file_selected_count = 0
       
        self.file_open_label = QLabel(f"Input path:")
        self.current_directory_label = QLabel(f"Current Directory: {self.current_directory}")
        self.output_file_label = QLabel(f"Output Path:")

        self.file_open_button = QPushButton("open file")
        self.file_open_button.clicked.connect(self.open_path_for_search_button)
        
        self.page_count_label = QLabel(f"Page Count: {self.page_count}")
        self.file_size_label = QLabel(f"Files Size: {self.file_size}")
        self.file_selected_count_label = QLabel(f"File Selected Count: {self.file_selected_count}")

        bottom_group_layout = QHBoxLayout()

        self.open_output_path_button = QPushButton("open output folder")
        self.open_output_path_button.clicked.connect(self.open_finder_window)

        self.open_output_log_button = QPushButton("open log")
        self.open_output_log_button.clicked.connect(self.open_log_window)

        # -----------------------
        # | tab | tab | tab | tab |
        # -----------------------
        self.tab_widget = QTabWidget()

        # ---------------
        # | Tab 1 layout |
        # ---------------
        tab_1_widget = QWidget() 
        tab_1_main = QHBoxLayout()
        tab_1_left = QVBoxLayout()
        tab_1_right = QVBoxLayout()
        
        tab_1_main.addLayout(tab_1_left)
        tab_1_main.addLayout(tab_1_right)
        tab_1_widget.setLayout(tab_1_main)
      

        # Create widgets tab1
        self.search_pdf_input_word = QLineEdit()
        self.search_pdf_input_word.setPlaceholderText("Open File to search")

        self.search_pdf_combo = QComboBox()
        self.search_pdf_combo.addItems(["0.9","0.8","0.7","0.6","0.5","0.4","0.3","0.2","0.1"])

        self.search_found_label = QLabel("Search Pending")

        self.search_pdf_button = QPushButton("fuzzy search")
        self.search_pdf_button.clicked.connect(self.search_pdf)
        self.search_pdf_button.setEnabled(False)

        self.search_save_pdf_label = QLabel("0 pages to merge")

        self.save_pdf_button = QPushButton("save")
        self.save_pdf_button.setEnabled(False)
        self.save_pdf_button.clicked.connect(self.save_pdf)

        tab_1_left.addWidget(self.file_open_label)
        tab_1_left.addWidget(self.search_pdf_input_word)
        tab_1_left.addWidget(self.search_found_label)
        tab_1_left.addWidget(self.search_save_pdf_label)

        tab_1_right.addWidget(self.file_open_button)
        tab_1_right.addWidget(self.search_pdf_combo)
        tab_1_right.addWidget(self.search_pdf_button)
        tab_1_right.addWidget(self.save_pdf_button)
        

        # ---------------
        # | Tab 2 layout |
        # ---------------
        tab2_content = QWidget()
        tab2_main = QHBoxLayout()
        tab2_left = QVBoxLayout()
        tab2_right = QVBoxLayout()
        tab2_right.setAlignment(Qt.AlignTop) 

        tab2_main.addLayout(tab2_left)
        tab2_main.addLayout(tab2_right)
        tab2_content.setLayout(tab2_main)

        self.page_number_input = QListWidget()
        self.page_number_input.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.page_number_input.setEnabled(False)
        self.page_number_input.itemSelectionChanged.connect(self.list_select)
        
        self.extract_pages_file_open_button = QPushButton("Open File")
        self.extract_pages_file_open_button.clicked.connect(self.open_path_to_extract_pages_button)
        
        self.split_pdf_save_file_button = QPushButton("Extract")
        self.split_pdf_save_file_button.setEnabled(False)
        self.split_pdf_save_file_button.clicked.connect(self.extract_pages)
        
        tab2_left.addWidget(self.page_number_input)
        tab2_right.addWidget(self.extract_pages_file_open_button, alignment=Qt.AlignTop)
        tab2_right.addWidget(self.split_pdf_save_file_button, alignment=Qt.AlignTop)

        # ---------------
        # | Tab 3 layout |
        # ---------------
        tab3_content = QWidget()
        tab3_main = QHBoxLayout()
        tab3_left = QVBoxLayout()
        tab3_right = QVBoxLayout()
        tab3_right.setAlignment(Qt.AlignTop)

        tab3_main.addLayout(tab3_left)
        tab3_main.addLayout(tab3_right)
        tab3_content.setLayout(tab3_main)

        self.file_list_display = QListWidget()
        self.file_list_display.setEnabled(False)

        join_pdf_label = QLabel("Join\\Combine Selected Files:\nChoose: PDF, PNG or PDF")
        self.join_pdf_select_multiple_files = QPushButton("Open Files")
        self.join_pdf_select_multiple_files.clicked.connect(self.open_files_to_join_button)

        self.auto_filename = QCheckBox("Auto Filename")
        self.auto_filename.setChecked(False)
        self.join_pdf_save_file_button = QPushButton("Save")
        self.join_pdf_save_file_button.setEnabled(False)
        self.join_pdf_save_file_button.clicked.connect(self.save_file_list)

        tab3_left.addWidget(self.file_list_display)
        tab3_right.addWidget(join_pdf_label)
        tab3_right.addWidget(self.join_pdf_select_multiple_files)
        tab3_right.addWidget(self.auto_filename)
        tab3_right.addWidget(self.join_pdf_save_file_button)

        # ---------------
        # | Tab 4 layout |
        # ---------------
        tab4_content = QWidget()
        tab4_main = QHBoxLayout()
        tab4_left = QVBoxLayout()
        
        tab4_right = QVBoxLayout()
        tab4_right.setAlignment(Qt.AlignTop)

        tab4_main.addLayout(tab4_left, 3)
        tab4_main.addLayout(tab4_right, 1)
        tab4_content.setLayout(tab4_main)

        self.extract_pdf_to_images_label = QLabel("PDF to Image:")
        self.extract_pdf_to_images_open_files_button = QPushButton("Open File")
        self.extract_pdf_to_images_open_files_button.clicked.connect(self.open_file_convert_pdf_to_image)
       
        self.pdf_to_image_page_count_label = QLabel("Pages:")
        self.extract_pdf_to_images_filetype = QComboBox()
        self.extract_pdf_to_images_filetype.addItems(["Filetype","jpg","png"])
        self.extract_pdf_to_images_filetype.currentIndexChanged.connect(self.pdf_to_image_button_check)
        self.extract_pdf_to_images_filetype.setEnabled(False)
        
        self.extract_pdf_to_images_quality = QComboBox()
        self.extract_pdf_to_images_quality.addItems(["Quality","High: 600dpi","Medium: 300dpi","Low: 150dpi"])
        self.extract_pdf_to_images_quality.currentIndexChanged.connect(self.pdf_to_image_button_check)
        self.extract_pdf_to_images_quality.setEnabled(False)

        self.extract_pdf_to_images_button = QPushButton("Extract to Images")
        self.extract_pdf_to_images_button.setEnabled(False)
        self.extract_pdf_to_images_button.clicked.connect(self.pdf_to_image_button)

        self.thread_manager = QThreadPool()

        tab4_left.addWidget(self.extract_pdf_to_images_label)
        tab4_left.addWidget(self.pdf_to_image_page_count_label)
        tab4_left.setAlignment(Qt.AlignTop)
        

        tab4_right.addWidget(self.extract_pdf_to_images_open_files_button)
        #self.extract_pdf_to_images_open_files_button.setFixedSize(QSize(150, 40))
        tab4_right.addWidget(self.extract_pdf_to_images_filetype)
        tab4_right.addWidget(self.extract_pdf_to_images_quality)
        tab4_right.addWidget(self.extract_pdf_to_images_button)

        
        # ---------------
        # | Tab 5 layout |
        # ---------------
        tab_5_content = QWidget()
        tab_5_main = QHBoxLayout()
        tab_5_left = QVBoxLayout()
        tab_5_left.setAlignment(Qt.AlignTop)
        
        tab_5_right = QVBoxLayout()
        tab_5_right.setAlignment(Qt.AlignTop)

        tab_5_main.addLayout(tab_5_left, 3)
        tab_5_main.addLayout(tab_5_right, 1)
        tab_5_content.setLayout(tab_5_main)

        self.extract_pdf_to_word_label = QLabel("PDF to Word:")
        tab_5_left.addWidget(self.extract_pdf_to_word_label)
        
        self.extract_pdf_to_word_open_files_button = QPushButton("Open File")
        self.extract_pdf_to_word_open_files_button.clicked.connect(self.open_file_dialog)
        tab_5_right.addWidget(self.extract_pdf_to_word_open_files_button)

        self.extract_pdf_to_word_label = QLabel("Extract")
        tab_5_left.addWidget(self.extract_pdf_to_word_label)

        self.extract_pdf_to_word_button = QPushButton("Word")
        self.extract_pdf_to_word_button.clicked.connect(self.convert_pdf_to_word)
        tab_5_right.addWidget(self.extract_pdf_to_word_button)

        self.extract_pdf_to_text_button = QPushButton("Text")
        self.extract_pdf_to_text_button.clicked.connect(lambda : self.ctr.extract_text(self.file_path))
        tab_5_right.addWidget(self.extract_pdf_to_text_button)

        
        # Add tabs to main tab widget
        self.tab_widget.addTab(tab_1_widget, "Search PDF")
        self.tab_widget.addTab(tab2_content, "Extract PDF")
        self.tab_widget.addTab(tab3_content, "Join Files")
        self.tab_widget.addTab(tab4_content, "File Conversions")
        self.tab_widget.addTab(tab_5_content, "PDF to Text")
        
        self.tab_widget.setFixedHeight(250)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        layout.addWidget(self.tab_widget, alignment=Qt.AlignTop)

        # ---------------
        # | Bottom panel |
        # ---------------
        bottom_draw_layout = QHBoxLayout()
        self.terminal_log = QTextEdit()
        self.terminal_log.setPlainText("log:")
        self.terminal_log.setFixedHeight(300)
        bottom_draw_layout.addWidget(self.terminal_log) 
        self.terminal_log.setVisible(False)
        
        bottom_group_layout.addWidget(self.output_file_label, alignment=Qt.AlignTop)
        bottom_group_layout.addWidget(self.open_output_log_button, alignment=Qt.AlignTop)
        bottom_group_layout.addWidget(self.open_output_path_button, alignment=Qt.AlignTop)
        
        self.setLayout(bottom_group_layout)
        layout.addLayout(bottom_group_layout)
        self.setLayout(bottom_draw_layout)
        layout.addLayout(bottom_draw_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # --- Rest of your class methods unchanged ---
    #
    def check_extract_selection_enabled(self):
        selected_items = self.page_number_input.selectedItems()
        if len(selected_items) > 0:
            self.split_pdf_save_file_button.setEnabled(True)
        else:
            self.split_pdf_save_file_button.setEnabled(False)
         
    #
    def clear_file_selection(self):
        self.file_path = ""
    #
    def open_log_window(self):
        self.display_sizes()
        if self.terminal_log.isVisible():
            self.terminal_log.hide()
            # do dynamically
            self.setFixedHeight(self.height()-314)
        else:
            self.setFixedHeight(self.height()+314)
            self.terminal_log.show()

    def open_finder_window(self):
        path = "output"
        """
        Opens a Finder window to the specified path on macOS.

        Args:
        path (str): The path to the directory or file to open in Finder.
        """
        try:
            subprocess.run(["open", path], check=True)
            print(f"Finder window opened to: {path}")
        except subprocess.CalledProcessError as e:
            print(f"Error opening Finder window: {e}")
        except FileNotFoundError:
            print("The 'open' command was not found. This script is intended for macOS.")

        # Example usage:
        # Open the current working directory in Finder
        #open_finder_window(".")

        # Open a specific directory
        # open_finder_window("/Users/yourusername/Documents")

        # Open a specific file and reveal it in Finder
        # open_finder_window("/Users/yourusername/Documents/my_document.txt")

    # 
    def tab_changed(self):
        print("new tab selected")
        self.clear_all_values()

    def list_select(self):
        print("item selected", self.page_number_input.selectedIndexes())
        self.terminal_log.append("new selection")
        for i in self.page_number_input.selectedIndexes():
            print("index:" , i.row())
            self.terminal_log.append(f"selected: {i.row()}")
    #
    # open file only. open files can be searched or converted so needs to be focused
    #
    def open_file_dialog(self):
        # Open a file dialog to select a single file

        last_directory = self.load_text("output/last_opened.txt")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",  # Dialog title
            str(last_directory),      # Initial directory (can be an empty string for default)
            "PDF Files (*.pdf);;All Files (*.*)" # File filters
        )
        if file_path:
            self.file_path = file_path
            print("file path open file dialog", file_path)
            self.save_text(file_path, "output/last_opened.txt")
            self.status_bar_label.setText("file path opened successfull")
        else:
            self.terminal_log.append("No file selected")
    #
    def update_labels(self, tab_name):
        
        if tab_name == "search":
            # sets search button enabled when file loaded. may not be text
            self.file_name = os.path.basename(self.file_path)
            self.file_open_label.setText(f"Input Path: {self.file_path}")
            self.current_directory = os.path.dirname(self.file_path)
            self.current_directory_label.setText(f"Current directory: {self.current_directory}")
            self.file_size = round(os.path.getsize(self.file_path)/1024/1024, 1)
            self.file_size_label.setText(f"Files Size: {self.file_size} MB")
            #
            # if pages found returns a count otherwise 0v
            #self.page_count = self.is_text_plus_num_pages
            self.terminal_log.append(f"Selected file: {self.file_path}")

        if tab_name == "extract":
            self.split_pdf_save_file_button.setEnabled(True)
            page_count = controller.MainController.count_pdf_pages(self, self.file_path)
            print("extract pages", page_count)
            # loads list of files
            if page_count > 0:
                for page in range(page_count):
                    self.page_number_input.addItem(str(page))
                self.page_number_input.setEnabled(True)
            else:
                self.status_bar_label.setText("file selection requires more than one page")
                self.split_pdf_save_file_button.setEnabled(False)
    #
    # 2 or more files can be joined
    # check if files are duplicate by hash
    #
    def open_multiple_files_dialog(self):

        #file_list = self.ctr.file_list
        #file_list = []
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Multiple Files",
            "",  # Current working directory
            "PDF Files (*.pdf);;JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*.*)"
        )
        # 
        if len(file_paths) > 1:
            #self.status_bar_label.setText(f"files selected")    
            #print("Selected files:")
            self.join_pdf_save_file_button.setEnabled(True)
            for path in file_paths:
                self.file_list.append(path)
            #
            # file dialog box that displays selected file paths for feedback
            #
            self.dialog = FeedbackWindow(self.file_list, self) # Pass self as parent for WindowModal
            if self.dialog.exec() == 1: # Shows the dialog modally
                self.terminal_log.append(f"multiple files selected")
                i = 1
                for file in self.file_list:
                    self.terminal_log.append(f"{i}: {os.path.basename(file)}")
                    i = i + 1
                # tab 3 join pdf    
                self.join_pdf_select_multiple_files.setText(f"File Selected Count: {len(self.file_list)}")
                
            else:
                self.terminal_log.append("File Operation Cancelled")
        else:
            self.status_bar_label.setText("files not selected")
    #
    # cut and paste example to be adapted
    #
    def save_file_dialog(self):
        # Open a QFileDialog for saving a file
        current_timestamp = time.time()
        if self.get_output_filename_flag() == True:
            filename = f"output/merge_{len(self.file_list)}_pages_{current_timestamp}.pdf"
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "output",  # Initial directory (empty string for default)
                "PDF Files (*.pdf);;All Files (*)" # File filters
            )
            print("return filename", filename)
        return filename

    # tab1 - search pdf - set search path
    def open_path_for_search_button(self):
        self.open_file_dialog()
        # update feedback labels
        self.is_text_plus_num_pages = self.ctr.check_pdf(self.file_path)
        if self.is_text_plus_num_pages > 0:
            self.search_pdf_button.setEnabled(True)
        else:
            self.ctr.check_if_ocr_required(self, self.is_text_plus_num_pages)
        self.update_labels("search")
    # tab 2
    def open_path_to_extract_pages_button(self):
        self.page_number_input.clear()
        self.open_file_dialog()
        # update feedback labels
        self.update_labels("extract")
    # tab 3
    def open_files_to_join_button(self):
        print("open files to join")
        self.open_multiple_files_dialog()
        self.file_list_display.addItems(self.file_list)

    # tab 4
    def open_file_convert_pdf_to_image(self):
        self.open_file_dialog()
        self.extract_pdf_to_images_label.setText(f"Pdf to Image file path: {self.file_path}")
        self.extract_pdf_to_images_filetype.setEnabled(True)
        self.extract_pdf_to_images_quality.setEnabled(True)
        num_pages = controller.MainController.count_pdf_pages(controller.MainController, self.file_path)
        self.pdf_to_image_page_count_label.setText(f"Pages to convert: {num_pages}")
        self.terminal_log.setText(f"Filepath: {self.file_path} loaded with {num_pages} pages")
        #self.extract_pdf_to_images_button.setText(f"Pages to convert: {num_pages}")
    # tab 5
    def convert_pdf_to_word(self):
        word_output = f"{self.file_path}.docx"
        controller.MainController.convert_pdf_to_word(word_output, self.file_path)
    #
    # check if image conversion buttons are selected
    #
    def pdf_to_image_button_check(self):
        #self.terminal_log.append("filetype/imagequality change")
        if self.extract_pdf_to_images_filetype.currentIndex() > 0 and self.extract_pdf_to_images_quality.currentIndex() > 0:
            self.extract_pdf_to_images_button.setEnabled(True)
        else:
            self.extract_pdf_to_images_button.setEnabled(False)

        if self.file_path == "":
            self.extract_pdf_to_images_button.setEnabled(False)

    # search button method
    def search_pdf(self):
        self.found_list = self.ctr.pdf_search(self, self.file_path, self.get_search_word(), self.get_level())
        if len(self.found_list) == 0:
            self.terminal_log.append("search result empty")
        self.search_save_pdf_label.setText(f"{len(self.found_list)} pages ready to merge")
    #
    def save_pdf(self):
        print(self.ctr.file_list)
        self.ctr.save_pdf(self, self.get_search_word(), self.found_list)

    # ------------------- #
    #  reset all values    #
    # --------------------#
    def clear_all_values(self):
        self.file_path = ""
        self.file_open_label.setText(f"Input path:")
        self.search_found_label.setText("Search Pending")
        self.search_save_pdf_label.setText(" 0pages ready to merge")
        self.output_file_label.setText("Output path:")
        self.status_bar_label.setText("")
        self.extract_pdf_to_images_label.setText("Input path:")
        self.page_number_input.clear()
        self.extract_pdf_to_images_filetype.setCurrentIndex(0)
        self.extract_pdf_to_images_quality.setCurrentIndex(0)
        self.extract_pdf_to_images_button.setEnabled(False)
    #
    #
    #
    def display_sizes(self):
        print("height", self.__class__ , self.height())

        

    def extract_pages(self):
        page_list = []
        #print(f"Selected Pages: {self.page_number_input.selectedIndexes()}")
        selection_model = self.page_number_input.selectionModel()
        # Get the selected indexes
        selected_indexes = selection_model.selectedIndexes()
    
        for index in selected_indexes:
            print("index appended ", index.row())
            page_list.append(index.row())
            print(f"Row: {index.row()}, Column: {index.column()}, Data: {index.data()}")
        # call extract and set output path
        self.output_file_label.setText(f"output path: {os.path.dirname(self.ctr.extract_pdfs(self, self.file_path, page_list))}")
    #
    def get_output_filename_flag(self):
        if self.auto_filename.isChecked():
            return True
        else:
            return False
    
    def save_file_list(self):
        file_name = self.save_file_dialog()
        controller.MainController.merge_pdfs(controller.MainController, self, file_name)
    
    def get_level(self):
        return self.search_pdf_combo.currentText()
    
    def get_search_word(self):
        return self.search_pdf_input_word.text()
    
    def pdf_to_image_button(self):
        filetype = self.extract_pdf_to_images_filetype.currentIndex()
        quality = self.extract_pdf_to_images_quality.currentIndex()
        #
        if filetype == 1:
            file_t = 'jpeg'
        else:
            file_t = 'png'
        #
        if quality == 1:
            dpi = 600
        elif quality == 3:
            dpi = 150
        else: 
            dpi = 300
        # called convert to images using thread
        out_path, count = self.thread_manager.connect(self.ctr.pdf_to_image(self, dpi, file_t))
        self.output_file_label.setText(f"Output path: {out_path}\nFiles converted: {count}")

    # use to save last folder accessed
    def save_text(self, output_path_text, output_path):
        dir_name = os.path.dirname(output_path_text)
        with open(output_path,'w') as file:
            file.write(dir_name)
    #
    def set_file_path(self, new_file_path):
        self.file_path = new_file_path

    # get text file data
    def load_text(self, filename):
        try:
            with open(filename, "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return "output"
  