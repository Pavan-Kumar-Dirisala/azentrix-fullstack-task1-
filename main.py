from rag.pdf_loader import extract_pages
from rag.chunker import chunk_text
def main():
    doc_path = "/Users/pavankumardirisala/D Drive/azentrix/RAMA.pdf"
    pages = extract_pages(doc_path)
    chunks = chunk_text(pages)
    print("Total pages = ", len(pages))
    print("Total chunks = ", len(chunks))
    for page in pages:
        print("=" * 60)
        print(f"PAGE {page['page']}")
        print("=" * 60)
        print(page["text"][:50])
        print("\n")   
    for chunk in chunks:
        print("=" * 60)
        print(f"CHUNK {chunk['chunk_id']}")
        print("=" * 60)
        print(chunk["content"][:50])
        print("\n")
if __name__ == "__main__":
    main()

