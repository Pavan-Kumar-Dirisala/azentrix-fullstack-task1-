def is_relevant(retrieved_chunks, threshold=20.0):

    if not retrieved_chunks:
        return False

    best_score = min(
        chunk["score"]
        for chunk in retrieved_chunks
    )

    return best_score <= threshold