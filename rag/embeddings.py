from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings_model():
    embeddings = HuggingFaceEmbeddings(
        model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    )
    return embeddings
        