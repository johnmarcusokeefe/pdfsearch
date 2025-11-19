from PySide6.QtWidgets import (
    QFileDialog
)
import time
from view import MainWindow

#
    # open file only. open files can be searched or converted so needs to be focused
    #
class FileDialogue:

    def __init__(self):
        super().__init__()

        
    # Open a file dialog to select a single file
    def open_file_dialog(self):
        
        #last_directory = self.load_text("output/last_opened.txt")
   
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open File",  # Dialog title
            "output",      # Initial directory (can be an empty string for default)
            "PDF Files (*.pdf);;All Files (*.*)" # File filters
        )
        print("open file dialog", file_path)
        return file_path

       

    
    def open_multiple_files_dialog(self):
        file_list = []
        file_list, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Multiple Files",
            "",  # Current working directory
            "PDF Files (*.pdf);;JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*.*)"
        )
        # 
        print("open multiple files", file_list )
        return file_list
    
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
    
    
    # get text file data
    def load_text(self, filename):
        try:
            with open(filename, "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return "output"
        
    # use to save last folder accessed
    def save_text(self, output_path_text, output_path):
        dir_name = os.path.dirname(output_path_text)
        with open(output_path,'w') as file:
            file.write(dir_name)