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

        # -------------------------
        # | tab | tab | tab | tab |
        # -------------------------
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
        tab_2_content = QWidget()
        tab_2_main = QHBoxLayout()
        tab_2_left = QVBoxLayout()
        tab_2_right = QVBoxLayout()
        tab_2_right.setAlignment(Qt.AlignTop) 

        tab_2_main.addLayout(tab_2_left)
        tab_2_main.addLayout(tab_2_right)
        tab_2_content.setLayout(tab_2_main)

        self.select_page_list = QListWidget()
        self.select_page_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.select_page_list.setEnabled(False)
        self.select_page_list.itemSelectionChanged.connect(self.list_select)
        
        self.extract_pages_file_open_button = QPushButton("Open File")
        
        self.split_pdf_save_file_button = QPushButton("Extract")
        self.split_pdf_save_file_button.setEnabled(False)
        
        tab_2_left.addWidget(self.select_page_list)
        tab_2_right.addWidget(self.extract_pages_file_open_button, alignment=Qt.AlignTop)
        tab_2_right.addWidget(self.split_pdf_save_file_button, alignment=Qt.AlignTop)

        # ---------------
        # | Tab 3 layout |
        # ---------------
        tab_3_content = QWidget()
        tab_3_main = QHBoxLayout()
        tab_3_left = QVBoxLayout()
        tab_3_right = QVBoxLayout()
        tab_3_right.setAlignment(Qt.AlignTop)

        tab_3_main.addLayout(tab_3_left)
        tab_3_main.addLayout(tab_3_right)
        tab_3_content.setLayout(tab_3_main)

        self.file_list_display = QListWidget()
        self.file_list_display.setEnabled(False)

        join_pdf_label = QLabel("Join\\Combine Selected Files:\nChoose: PDF, PNG or PDF")
        self.join_pdf_select_multiple_files = QPushButton("Select Files")
        self.auto_filename = QCheckBox("Auto Filename")
        self.auto_filename.setChecked(False)
        self.join_pdf_save_file_button = QPushButton("Merge Files")
        self.join_pdf_save_file_button.setEnabled(False)

        tab_3_left.addWidget(self.file_list_display)
        tab_3_right.addWidget(join_pdf_label)
        tab_3_right.addWidget(self.join_pdf_select_multiple_files)
        tab_3_right.addWidget(self.auto_filename)
        tab_3_right.addWidget(self.join_pdf_save_file_button)

        # ---------------
        # | Tab 4 layout |
        # ---------------
        tab_4_content = QWidget()
        tab_4_main = QHBoxLayout()
        tab_4_left = QVBoxLayout()
        
        tab_4_right = QVBoxLayout()
        tab_4_right.setAlignment(Qt.AlignTop)

        tab_4_main.addLayout(tab_4_left, 3)
        tab_4_main.addLayout(tab_4_right, 1)
        tab_4_content.setLayout(tab_4_main)

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

        tab_4_left.addWidget(self.extract_images_from_pdf_label)
        tab_4_left.addWidget(self.extract_images_from_pdf_count_label)
        tab_4_left.setAlignment(Qt.AlignTop)
        
        tab_4_right.addWidget(self.extract_images_from_pdf_open_file_button)
        tab_4_right.addWidget(self.extract_images_from_pdf_filetype_combo)
        tab_4_right.addWidget(self.extract_images_from_pdf_quality_combo)
        tab_4_right.addWidget(self.extract_images_from_pdf_run_button)

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

        # ---------------
        # | Tab 6 layout |
        # ---------------
        # Add tabs to main tab widget
        self.tab_widget.addTab(tab_1_widget, "Search")
        self.tab_widget.addTab(tab_2_content, "Extract Pages")
        self.tab_widget.addTab(tab_3_content, "Append Files")
        self.tab_widget.addTab(tab_4_content, "PDF -> Image")
        self.tab_widget.addTab(tab_5_content, "PDF -> Text")
        
        self.tab_widget.setFixedHeight(300)

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
            print("tab widget height", self.tab_widget.height())
            self.setFixedHeight(self.height()-314)
        else:
            self.setFixedHeight(self.height()+314)
            self.terminal_log.show()
    #
    # tab 2
    #
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
            self.terminal_log.append(f"Selected file: {file_path}")
    #
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