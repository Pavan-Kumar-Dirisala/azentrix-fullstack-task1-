from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embeddings_model

def vector_storage(chunks):
    embeddings = get_embeddings_model()
    texts=[]
    metadatas=[]

    for chunk in chunks:
        texts.append(chunk["content"])
        metadatas.append(
            {
                "chunk_id" : chunk["chunk_id"],
                "page" : chunk["page"]
            }
        )
    vector_store = FAISS.from_texts(
        texts = texts,
        embedding = embeddings,
        metadatas = metadatas
    )
    return vector_store