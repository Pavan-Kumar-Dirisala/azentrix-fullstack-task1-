from rag.pdf_loader import extract_pages

def main():
    doc_path = "/Users/pavankumardirisala/D Drive/azentrix/RAMA.pdf"
    pages = extract_pages(doc_path)
    
    print("Total pages = ", len(pages))
    for page in pages:
        print("=" * 60)
        print(f"PAGE {page['page']}")
        print("=" * 60)
        print(page["text"][:300])
        print("\n")   
if __name__ == "__main__":
    main()

