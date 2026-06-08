from rag.pdf_loader import extract_pages


def load_documents(pdf_paths):

    all_pages = []

    for pdf_path in pdf_paths:

        pages = extract_pages(pdf_path)

        all_pages.extend(pages)

    return all_pages