from PySide6.QtWidgets import (
    QFileDialog
)
import time

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

        return file_path

    
    def open_multiple_file_dialog(self):
        file_list = []
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
                file_list.append(path)
            #
            # file dialog box that displays selected file paths for feedback
            #
            self.dialog = FeedbackWindow(self.file_list, self) # Pass self as parent for WindowModal
            if self.dialog.exec() == 1: # Shows the dialog modally
                self.terminal_log.append(f"multiple files selected")
                i = 1
                for file in file_list:
                    self.terminal_log.append(f"{i}: {os.path.basename(file)}")
                    i = i + 1
                # tab 3 join pdf    
                self.join_pdf_select_multiple_files.setText(f"File Selected Count: {len(self.file_list)}")
                
            else:
                self.terminal_log.append("File Operation Cancelled")
        else:
            self.status_bar_label.setText("files not selected")

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