def retriever(vector_db , query , k = 3):
    results = vector_db.similarity_search_with_score(
        query = query,
        k = k
    )
    retrived_chunks = []
    
    for doc , score in results:
        retrived_chunks.append(
            {
                "chunk_id" : doc.metadata["chunk_id"],
                "page" : doc.metadata["page"],
                "score" : float(score),
                "content" : doc.page_content
            }
        )
    return retrived_chunks
            