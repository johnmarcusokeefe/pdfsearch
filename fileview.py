# fileview.py
from PySide6.QtWidgets import (
    QFileDialog
)
import os
#
# file dialogues
#
class FileDialogue:

    def __init__(self):
        super().__init__()
    #
    # user selects the directory
    #
    def open_folder_dialog(self):
        
        folder_path = QFileDialog.getExistingDirectory(
            None,
            "Select Folder",  # Dialog title
            str(self.last_path_opened)      # Last folder opened
        )

    def open_folder_dialog(self):
        
        folder_path = QFileDialog.getExistingDirectory(
            None,
            "Select Folder",  # Dialog title
            str(self.last_path_opened)      # Last folder opened
        )
        return folder_path
    #    
    # Open a file dialog to select a single file
    #
    def open_file_dialog(self):
        
        file_path = ""
        self.last_path_opened = self.load_text()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open File",  # Dialog title
            str(self.last_path_opened),      # Initial directory (can be an empty string for default)
            "PDF Files (*.pdf);;All Files (*.*)" # File filters
        )
        print("set filepath", file_path)
        self.save_text(file_path)
        return file_path
    #
    # return file list
    #
    def open_multiple_files_dialog(self):

        file_list = []
        self.last_path_opened = self.load_text()
        file_list, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Multiple Files",
            str(self.last_path_opened),  # Current working directory
            "PDF Files (*.pdf);;JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*.*)"
        )
        # 
        print("open multiple files", file_list)
        #
        return file_list
    
    #
    # cut and paste example to be adapted
    # todo: separate the get name from the createfilename. create filename in control
    def user_filename_input_dialog(self):
        # Open a QFileDialog for saving a file
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save File",
            "output",  # Initial directory (empty string for default)
            "PDF Files (*.pdf);;All Files (*)" # File filters
        )
        return filename
    #
    # get text file data
    #
    def load_text(self):
        try:
            with open("saved_path.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            output_path = "/"
            self.save_text(output_path)
            return output_path
    #   
    # use to save last folder accessed
    #
    def save_text(self, output_path):
        file_name = "saved_path.txt"
        try:
            with open(file_name,'w') as file:
                file.write(os.path.dirname(output_path))
            print("path saved")
        except:
            print("failed to save path")

