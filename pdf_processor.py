import PyPDF2
import os

def extract_pages_with_keyword(pdf_path, keyword):
    output_pdf_path = pdf_path.replace('.pdf', '_filtered.pdf')
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        for page in range(len(reader.pages)):
            text = reader.pages[page].extract_text()
            if keyword.lower() in text.lower():
                writer.add_page(reader.pages[page])

        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)

    return output_pdf_path
