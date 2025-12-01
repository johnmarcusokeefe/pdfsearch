# view.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QDialog, QCheckBox, QTabWidget, QLineEdit, QComboBox,
    QAbstractItemView, QTextEdit
)
from PySide6.QtCore import Qt, QRegularExpression
import os, subprocess

from PySide6.QtGui import QRegularExpressionValidator


class FeedbackWindow(QDialog):

   def __init__(self, file_list):
        self.file_list = file_list
        super().__init__()

        self.setWindowTitle("Feedback Window")
        layout = QVBoxLayout(self)

        label = QLabel("Files Selected:")
        self.list_widget = QListWidget()
        i = 0
        
        for line in self.file_list:
            self.list_widget.addItem(str(os.path.basename(line)))
            i = i + 1

        layout.addWidget(self.list_widget)

        accept_button = QPushButton("Add Files")
        accept_button.clicked.connect(self.accept) # Connect to accept or reject to close the dialog
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(accept_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)
        

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Scan and Search")
        
        self.custom_file_name = ""
    
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
    
        self.current_directory_label = QLabel(f"Current Directory: {self.current_directory}")
        self.output_file_label = QLabel(f"Output Path:")
        
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
        
        self.search_open_file_label = QLabel(f"Input path:")
        self.search_open_file_button = QPushButton("open file")
        
        self.search_pdf_input_word = QLineEdit()
        self.search_pdf_input_word.setPlaceholderText("enter single word without spaces")
        
          # Create a QRegExp that matches any character except a space
        # The '+' means one or more occurrences of the allowed characters
        regex = QRegularExpression("[^ ]+") 
        
        # Create a QRegExpValidator with the defined regex
        validator = QRegularExpressionValidator(regex)
        
        # Set the validator on the QLineEdit
        self.search_pdf_input_word.setValidator(validator)

        self.search_pdf_combo = QComboBox()
        self.search_pdf_combo.addItems(["0.9","0.8","0.7","0.6","0.5","0.4","0.3","0.2","0.1"])
        self.search_pdf_combo.setEnabled(False)
        self.search_found_label = QLabel("Search Pending")

        
        self.search_pdf_button = QPushButton("fuzzy search")
        self.search_pdf_button.setEnabled(False)

        self.ocr_pdf_button = QPushButton("ocr pdf")
        self.ocr_pdf_button.setEnabled(False)
        self.ocr_pdf_label = QLabel("OCR Pending")

        self.search_save_pdf_label = QLabel("0 pages to merge")

        self.save_pdf_button = QPushButton("save")
        self.save_pdf_button.setEnabled(False)
        #self.save_pdf_button.clicked.connect(self.save_pdf)

        tab_1_left.addWidget(self.search_open_file_label)
        tab_1_left.addWidget(self.ocr_pdf_label)
        tab_1_left.addWidget(self.search_pdf_input_word)
        tab_1_left.addWidget(self.search_found_label)
        tab_1_left.addWidget(self.search_save_pdf_label)

        tab_1_right.addWidget(self.search_open_file_button)
        tab_1_right.addWidget(self.ocr_pdf_button)
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

        self.select_page_list = QListWidget()
        self.select_page_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.select_page_list.setEnabled(False)
        self.select_page_list.itemSelectionChanged.connect(self.list_select)
        
        self.extract_pages_file_open_button = QPushButton("Open File")
        #self.extract_pages_file_open_button.clicked.connect(self.open_path_to_extract_pages_button)
        
        self.split_pdf_save_file_button = QPushButton("Extract")
        self.split_pdf_save_file_button.setEnabled(False)
        #self.split_pdf_save_file_button.clicked.connect(self.extract_pages)
        
        tab2_left.addWidget(self.select_page_list)
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
        self.join_pdf_select_multiple_files = QPushButton("Select Files")
        #self.join_pdf_select_multiple_files.clicked.connect(self.open_files_to_join_button)
        self.auto_filename = QCheckBox("Auto Filename")
        self.auto_filename.setChecked(False)
        self.join_pdf_save_file_button = QPushButton("Merge Files")
        self.join_pdf_save_file_button.setEnabled(False)
        #self.join_pdf_save_file_button.clicked.connect(self.save_file_list)
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

        self.extract_images_from_pdf_label = QLabel("PDF to Image:")
        self.extract_images_from_pdf_open_file_button = QPushButton("Open File")
       
        self.extract_images_from_pdf_count_label = QLabel("Pages:")
        self.extract_images_from_pdf_filetype_combo = QComboBox()
        self.extract_images_from_pdf_filetype_combo.addItems(["Filetype","jpg","png"])
        self.extract_images_from_pdf_filetype_combo.setEnabled(False)
        
        self.extract_images_from_pdf_quality_combo = QComboBox()
        self.extract_images_from_pdf_quality_combo.addItems(["Quality","High: 600dpi","Medium: 300dpi","Low: 150dpi"])
        self.extract_images_from_pdf_quality_combo.setEnabled(False)

        self.extract_images_from_pdf_run_button = QPushButton("Extract to Images")
        self.extract_images_from_pdf_run_button.setEnabled(False)

        tab4_left.addWidget(self.extract_images_from_pdf_label)
        tab4_left.addWidget(self.extract_images_from_pdf_count_label)
        tab4_left.setAlignment(Qt.AlignTop)
        
        tab4_right.addWidget(self.extract_images_from_pdf_open_file_button)
        #self.extract_pdf_to_images_open_files_button.setFixedSize(QSize(150, 40))
        tab4_right.addWidget(self.extract_images_from_pdf_filetype_combo)
        tab4_right.addWidget(self.extract_images_from_pdf_quality_combo)
        tab4_right.addWidget(self.extract_images_from_pdf_run_button)
        # ---------------
        # | Tab 5 layout |
        # ---------------
        tab_5_content = QWidget()
        tab_5_main = QHBoxLayout()
        tab_5_left = QVBoxLayout()
        tab_5_left.setAlignment(Qt.AlignTop)
        tab_5_left.setAlignment(Qt.AlignTop)
        
        tab_5_right = QVBoxLayout()
        tab_5_right.setAlignment(Qt.AlignTop)

        tab_5_main.addLayout(tab_5_left, 3)
        tab_5_main.addLayout(tab_5_right, 1)
        tab_5_content.setLayout(tab_5_main)

        self.extract_pdf_to_word_label = QLabel("Extract PDF Content:")
        self.extract_pdf_open_file_button = QPushButton("Open File")
        
        self.extract_pdf_to_word_content_button = QPushButton("Convert to Word")
        self.extract_pdf_to_word_content_button.setEnabled(False)
        self.extract_pdf_to_text_button = QPushButton("Convert to Text")
        self.extract_pdf_to_text_button.setEnabled(False)

        tab_5_left.addWidget(self.extract_pdf_to_word_label)
        tab_5_right.addWidget(self.extract_pdf_open_file_button)
        tab_5_right.addWidget(self.extract_pdf_to_word_content_button)
        tab_5_right.addWidget(self.extract_pdf_to_text_button)

        # Add tabs to main tab widget
        self.tab_widget.addTab(tab_1_widget, "Search")
        self.tab_widget.addTab(tab2_content, "Extract Pages")
        self.tab_widget.addTab(tab3_content, "Append Files")
        self.tab_widget.addTab(tab4_content, "PDF -> Image")
        self.tab_widget.addTab(tab_5_content, "PDF -> Text")
        
        self.tab_widget.setFixedHeight(250)
        self.tab_widget.currentChanged.connect(self.tab_change)

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

    #
    # tab 2
    #
    def check_extract_selection_enabled(self):
        selected_items = self.select_page_list.selectedItems()
        if len(selected_items) > 0:
            self.split_pdf_save_file_button.setEnabled(True)
        else:
            self.split_pdf_save_file_button.setEnabled(False)
    #
    # toggle log window open/closed
    #
    def open_log_window(self):
        if self.terminal_log.isVisible():
            self.terminal_log.hide()
            # do dynamically
            self.setFixedHeight(self.height()-314)
        else:
            self.setFixedHeight(self.height()+314)
            self.terminal_log.show()
    
    # 
    def tab_change(self):
        print("new tab selected",self.tab_widget.currentIndex()+1)
        self.clear_all_values()
        
    # tab 2
    def list_select(self):
        print("item selected", self.select_page_list.selectedIndexes())
        self.terminal_log.append("new selection")
        for i in self.select_page_list.selectedIndexes():
            print("index:" , i.row())
            self.terminal_log.append(f"selected: {i.row()}")
    #
    def update_labels(self, tab_name, file_path):
        
        if tab_name == "search":
            # sets search button enabled when file loaded. may not be text
            self.file_name = os.path.basename(file_path)
            self.search_open_file_label.setText(f"Input Path: {file_path}")
            self.current_directory = os.path.dirname(file_path)
            self.current_directory_label.setText(f"Current directory: {self.current_directory}")
            self.file_size = round(os.path.getsize(file_path)/1024/1024, 1)
            self.file_size_label.setText(f"Files Size: {self.file_size} MB")
            #
            # if pages found returns a count otherwise 0v
            #self.page_count = self.is_text_plus_num_pages
            self.terminal_log.append(f"Selected file: {file_path}")
    #
    # tab 4
    def open_file_convert_pdf_to_image(self):
        #file_path = self.filedialog.open_file_dialog()
        # self.extract_pdf_to_images_label.setText(f"Pdf to Image file path: {file_path}")
        #self.extract_pdf_to_images_filetype.setEnabled(True)
        self.extract_images_from_pdf_quality_combo.setEnabled(True)
        # num_pages = self.ctl.count_pdf_pages(file_path)
        # self.pdf_to_image_page_count_label.setText(f"Pages to convert: {num_pages}")
        # self.terminal_log.setText(f"Filepath: {file_path} loaded with {num_pages} pages")
        #self.extract_pdf_to_images_button.setText(f"Pages to convert: {num_pages}")
   
    # tab 5
    def convert_pdf_to_word(self):
        word_output = f"{self.file_path}.docx"
        #MainController.convert_pdf_to_word(word_output, self.file_path)
 
    
    # ------------------- #
    #  reset all values    #
    # --------------------#
    def clear_all_values(self):
        self.file_path = ""
        self.search_found_label.setText("Search Pending")
        self.search_save_pdf_label.setText("0 pages ready to merge")
        self.output_file_label.setText("Output path:")
        self.status_bar_label.setText("")
        #self.extract_images_from_pdf_label.setText("Open File:")
        self.select_page_list.clear()
        self.extract_images_from_pdf_filetype_combo.setCurrentIndex(0)
        self.extract_images_from_pdf_quality_combo.setCurrentIndex(0)
        self.extract_images_from_pdf_run_button.setEnabled(False)

    #
    # 
    #
    def get_output_filename_flag(self):
        if self.auto_filename.isChecked():
            return True
        else:
            return False
  
    
    def get_level(self):
        return self.search_pdf_combo.currentText()
    
    def get_search_word(self):
        return self.search_pdf_input_word.text()
    
    def pdf_to_image_button(self):
        filetype = self.extract_images_from_pdf_filetype_combo.currentIndex()
        quality = self.extract_images_from_pdf_quality_combo.currentIndex()
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
        out_path, count = self.ctr.pdf_to_image(self, dpi, file_t)
        self.output_file_label.setText(f"Output path: {out_path}\nFiles converted: {count}")

    #
    #
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