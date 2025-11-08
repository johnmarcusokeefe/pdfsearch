import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from pypdf import *
import os
import Levenshtein as levenshtein
import ocrmypdf
from tkinter import Text

# global variables
file_path = None
search_string = None
reader = None
fuzzy_checkbox = None
file_name = None
page_list = []
file_list = []

# use to save last folder accessed
def save_input(data, filename, option):
	with open(filename, option) as file:
		file.write(data + "\n")
          

# get text file data
def load_input(filename):
	try:
		with open(filename, "r") as file:
			return [line.strip() for line in file.readlines()]
	except FileNotFoundError:
		return []


# open pdf file using gui dialog
def open_file():
    global file_path, reader, file_name
    
    file_path = filedialog.askopenfilename(
        title="Select a file",
        initialdir=load_input("output/last_opened.txt"),  # Optional: set initial directory, returns an array but this works
        filetypes=[("PDF", "*.pdf"), ("All files", "*.*")] # Optional: filter file types
    )
    if file_path:
        print(f"Selected file: {file_path}")
        # saves the last directory path from file opened
        save_input(os.path.dirname(file_path), "output/last_opened.txt", "w")
        file_name = os.path.basename(file_path)
        file_label_text.set(file_name)
        # You can now open and process the file content
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            # search text on page and if text found create an array of page numbers
            if text == "":
                print("file requires OCR")
                ocr_button.config(state=tk.NORMAL)
                ocr_feedback_text.set("click OCR button to make searchable")
            else:
                search_button.config(state=tk.NORMAL)
        display_label.config(text=f"Selected: {os.path.basename(file_path)}") # Update Label text
        page_num_label.config(text=f"No of pages: {num_pages}") # Update Label text
    


def ocr_pdf():
    global file_path, file_name, page_list, search_string
    """
    Adds an OCR text layer to a scanned PDF, making it searchable.
    """
    output_pdf_path = "output/ocr_"+file_name
    ocrmypdf.ocr(file_path, output_pdf_path, skip_text=True, oversample=600, clean=True)
    print(f"OCR completed. Searchable PDF saved to: {output_pdf_path}")
    file_path = output_pdf_path
    file_label_text.set(file_path)
    search_button.config(state=tk.NORMAL)
    

# force_ascii=True, full_process=True
def fuzzy_pdf_search(text, page_num):
    found = 0
    for word in text.split():
        l_ratio = levenshtein.ratio(search_string.get().lower(), word.lower())
        if l_ratio > float(fuzzy_option.get()):
            # return this page as match
            print("word, option, page number", word, fuzzy_option.get(), page_num)
            log_text.insert(INSERT,"search: " + search_string.get() + " found: " +word+ " page no: "+str(page_num)+" ratio: "+ str(round(l_ratio, 2)) +"\n")
            found = 1

    return found


def pdf_search():
    global file_path, search_string, reader, fuzzy_checkbox, page_list
    page_list = []
    print("pdf search", file_path, search_string.get())
    reader = PdfReader(file_path)
    num_pages = len(reader.pages)
    # loop through pages
    
    log_text.delete("1.0", END)
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        if fuzzy_pdf_search(text, page_num) > 0:
            save_button.config(state=tk.NORMAL)
            page_list.append(page_num)
        # search text on page and if text found create an array of page numbers
            # if text.lower().find(search_string.get().lower()) != -1:
            #     print("text found on page ", page_num)
               #print(text)
        
    print("pages ", page_list)
    found_label_text.set("Search found: "+str(len(page_list)));


# todo: option to attach to existing file
def pdf_save():
    # all files saved to output
    global file_path, page_list
    if len(page_list) > 0:
        writer = PdfWriter()
        for page in page_list:
            writer.add_page(reader.pages[page])
        with open("output/"+search_string.get()+".pdf", "wb") as output_pdf:
            writer.write(output_pdf)

        print("Pages extracted successfully!")


# need to check if multiple files selected
def select_multiple_files():
    global file_list

    file_paths = filedialog.askopenfilenames(
        title="Select multiple files",
        filetypes=(("PDF Files", "*.pdf"), ("All files", "*.*"))
    )

    if file_paths:
        log_text.insert(INSERT,"files selected \n")
        print("Selected files:")
        for path in file_paths:
            file_list.append(path)
            log_text.insert(INSERT,"path: " + path +"\n")
            print(file_list)
            

#
def merge_pdfs():
    global file_list

    output_filename = joined_pdf_string.get()+".pdf"
    print("call merge pdfs")
    """
    Merges a list of PDF files into a single output PDF.
    """
    for path in file_list:
        print(path)
        merger = PdfWriter()

        for pdf_file in file_list:
            merger.append(pdf_file)

        with open("output/"+output_filename, "wb") as output_file:
            merger.write(output_file)

        merger.close()
        print(f"PDFs merged successfully into {output_filename}")


#
def clear_log():
    """Clears the content of the Text widget."""
    log_text.delete("1.0", tk.END)

# display elements
root = tk.Tk()
root.title("PDFSearch")
root.geometry("600x800") # Initial size

 # Make the central column and row expandable
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.configure(bg="#B8B4A3") 


# Create a frame to hold content
content_frame = tk.Frame(root, bg="#B8B4A3")
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=0)
content_frame.columnconfigure(2, weight=0)
content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20) # Center the frame


# Create a Label widget for displaying the output
file_label_text = tk.StringVar()
file_label_text.set("no file selected")

ocr_feedback_text = tk.StringVar()
ocr_feedback_text.set("ocr report")


# open 
display_label = tk.Label(content_frame, textvariable=file_label_text, bg="white")
display_label.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)

page_num_label = tk.Label(content_frame, text="page count: 0", bg="#B8B4A3")
page_num_label.grid(row=0, column=1, sticky=NSEW, padx=5, pady=5)

open_button = tk.Button(content_frame, text="open file", command=open_file, width=8)
open_button.grid(row=0, column=2, sticky="e", padx=5, pady=5)


# ocr
ocr_label = Label(content_frame, text="OCR PDF:", bg="#B8B4A3", fg="white", justify="left")
ocr_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

ocr_display_label = tk.Label(content_frame, textvariable=ocr_feedback_text,  bg="white", anchor=W)
ocr_display_label.grid(row=2, column=0, columnspan=2, sticky=W+E, padx=5, pady=5)

ocr_button = tk.Button(content_frame, text="ocr", command=ocr_pdf, width=8)
ocr_button.config(state=tk.DISABLED)
ocr_button.grid(row=2, column=2, sticky="e", padx=5, pady=5)


# search
search_label = Label(content_frame, text="Search PDF:", bg="#B8B4A3", fg="white", justify="left")
search_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")


search_string = tk.StringVar()
search_string.set("enter text")
search_entry = tk.Entry(content_frame, textvariable=search_string)
search_entry.grid(row=4, column=0, sticky=NSEW, padx=5, pady=5)

fuzzy_option = tk.StringVar()
fuzzy_option.set(0.9)  # Set initial value
fuzzy_options = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1]

fuzzy_combo = ttk.Combobox(content_frame, textvariable=fuzzy_option, values=fuzzy_options, width=10, background="red")
fuzzy_combo.grid(row=4, column=1, sticky=W, padx=5, pady=5)

search_button = tk.Button(content_frame, text="search", command=pdf_search, width=8)
search_button.config(state=tk.DISABLED)
search_button.grid(row=4, column=2, sticky="e", padx=5, pady=5)

# search
search_label = Label(content_frame, text="Save pages found:", bg="#B8B4A3", fg="white", justify="left")
search_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

found_label_text = tk.StringVar()
found_label_text.set("Search result: 0") # Set initial value
found_label = tk.Label(content_frame, text="0", textvariable=found_label_text, bg="white")
found_label.grid(row=6, column=0, columnspan=2, sticky=NSEW, padx=5, pady=5)

save_button = tk.Button(content_frame, text="save extracted pages", command=pdf_save)
save_button.config(state=tk.DISABLED)
save_button.grid(row=6, column=2, sticky=NSEW, padx=5, pady=5)

horizontal_separator = ttk.Separator(content_frame, orient=tk.HORIZONTAL)
horizontal_separator.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

pdf_labels = tk.Label(content_frame, text="PDF Join Utility:", bg="#B8B4A3", fg="white", justify="left")
pdf_labels.grid(row=8, column=0, padx=5, pady=5, sticky="w")

joined_pdf_string= tk.StringVar()
joined_pdf_string.set("new_filename")
joined_pdf_name = tk.Entry(content_frame, textvariable=joined_pdf_string)
joined_pdf_name.grid(row=9, column=0, sticky=NSEW, padx=5, pady=5)

select_files_button = tk.Button(content_frame, text="select files", command=select_multiple_files )
select_files_button.grid(row=9, column=1, sticky="w")

join_files_button = tk.Button(content_frame, text="join files", command=merge_pdfs, width=8)
join_files_button.grid(row=9, column=2, sticky="e")

horizontal_separator2 = ttk.Separator(content_frame, orient=tk.HORIZONTAL)
horizontal_separator2.grid(row=10, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

log_labels = tk.Label(content_frame, text="Log output:", bg="#B8B4A3", fg="white", justify="left")
log_labels.grid(row=11, column=0, padx=5, pady=5, sticky="w")

log_text = tk.Text(content_frame, wrap=tk.WORD)
log_text.grid(row=12, column=0, columnspan=3, sticky=NSEW, padx=5, pady=5)

clear_log_button = tk.Button(content_frame, text="clear log", command=clear_log)
clear_log_button.grid(row=13, column=2, sticky="e")

content_frame.mainloop()