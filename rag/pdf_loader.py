import fitz
import os

def extract_pages(pdf_path: str) -> list:
    document = fitz.open(pdf_path)
    file_name = os.path.basename(pdf_path)

    pages = []
    for page_number in range(len(document)):
        page = document.load_page(page_number)
        text = page.get_text().strip()
        if text:
            pages.append(
                {
                    "page": page_number + 1,
                    "source": file_name,
                    "text": text
                }
            )
    document.close()
    return pages