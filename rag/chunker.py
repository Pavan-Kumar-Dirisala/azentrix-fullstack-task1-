from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(pages: list):
    chunker = RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap = 100)

    chunks =[]
    chunk_index = 1

    for page in pages:
        page_number = page['page']
        text = page['text']
        page_chunks = chunker.split_text(text)
        for chunk in page_chunks:
            chunks.append(
                {
                    'chunk_id' : chunk_index,
                    'page': page_number,
                    'content' : chunk
                }
            )
            chunk_index += 1
    return chunks
    