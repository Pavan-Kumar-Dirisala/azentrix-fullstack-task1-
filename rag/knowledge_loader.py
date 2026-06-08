from rag.document_loader import load_documents
from rag.text_loader import extract_text_input


def load_knowledge(
    pdf_paths=None,
    text=None
):

    pages = []

    if pdf_paths:
        pages.extend(
            load_documents(pdf_paths)
        )

    if text:
        pages.extend(
            extract_text_input(text)
        )

    return pages