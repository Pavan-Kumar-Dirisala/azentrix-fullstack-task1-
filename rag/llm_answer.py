from rag.llm_initializer import openai
from rag.prompts import SYSTEM_PROMPT


def answer(query, retrieved_chunks):

    context = "\n\n".join(
        chunk["content"]
        for chunk in retrieved_chunks
    )

    messages = [
        (
            "system",
            SYSTEM_PROMPT
        ),
        (
            "user",
            f"""
Context:

{context}

Question:

{query}
"""
        )
    ]

    response = openai.invoke(messages)

    citations = []

    for chunk in retrieved_chunks:

        citations.append(
            f"Source {chunk['source']} | Page {chunk['page']}"
        )

    citations = "\n".join(
        f"[{i}] {citation}"
        for i, citation in enumerate(
            citations,
            start=1
        )
    )

    return (
        f"{response.content}\n\n"
        f"Sources:\n{citations}"
    )