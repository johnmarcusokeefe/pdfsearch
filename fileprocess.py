import pypdfium2 as pdfium
import pytesseract

class ExtractText:

   
    def extract_text(self, file_path, page_list, ctl):
        
        # print("fileprocess filepath",file_path)
        if file_path:

            pdf = pdfium.PdfDocument(file_path)
            for i, page in enumerate(pdf):
                img = page.render(scale=300/72).to_pil()
                text = pytesseract.image_to_string(img)
                # print(f"--- Start Page {i+1} ---")
                # print(text)
                page_list.append(text)
                # print(f"page number {i}")
                # with open("output/test.txt", 'a') as f:
                #     f.write(text+"\n **end page** \n")
                ctl.set_status_bar(f"running ocr page no: {i}")
            print("text extracted")
            ctl.set_status_bar("text extracted")
            ctl._view.search_pdf_button.setEnabled(True)
            ctl._view.search_pdf_combo.setEnabled(True)    
            #print(page_list)
            
   