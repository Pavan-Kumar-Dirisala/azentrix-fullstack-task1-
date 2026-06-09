from rag.pdf_loader import extract_pages


def load_documents(pdf_files):

    all_pages = []

    for pdf in pdf_files:

        pages = extract_pages(
            pdf["path"],
            pdf["name"]
        )

        all_pages.extend(pages)

    return all_pages