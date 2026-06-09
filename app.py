import tempfile
import streamlit as st

from rag.knowledge_loader import load_knowledge
from rag.chunker import chunk_text
from rag.vector_store import vector_storage
from rag.retriver import retriever
from rag.llm_answer import answer

st.set_page_config(
    page_title="Context-Aware Document Q&A Bot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Context-Aware Document Q&A Bot")
st.caption(
    "Upload PDFs or paste text and ask questions."
)

# ---------------------------------
# Session State
# ---------------------------------

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_summary" not in st.session_state:
    st.session_state.document_summary = ""

# ---------------------------------
# Sidebar
# ---------------------------------

with st.sidebar:

    st.header("Knowledge Source")

    uploaded_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    pasted_text = st.text_area(
        "Or Paste Text",
        height=200
    )

    process = st.button(
        "🚀 Process Knowledge Base",
        use_container_width=True
    )

    clear = st.button(
        "🗑️ Clear Session",
        use_container_width=True
    )

# ---------------------------------
# Clear Session
# ---------------------------------

if clear:

    st.session_state.vector_db = None
    st.session_state.documents_loaded = False
    st.session_state.messages = []
    st.session_state.document_summary = ""

    st.rerun()

# ---------------------------------
# Process Documents
# ---------------------------------

if process:

    if not uploaded_files and not pasted_text.strip():

        st.warning(
            "Please upload PDF files or paste text."
        )

    else:

        try:

            pdf_files = []

            for uploaded_file in uploaded_files:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:

                    tmp.write(
                        uploaded_file.read()
                    )

                    pdf_files.append(
                        {
                            "path": tmp.name,
                            "name": uploaded_file.name
                        }
                    )

            pages = load_knowledge(
                pdf_paths=pdf_files,
                text=pasted_text
            )

            with st.spinner(
                "Building knowledge base..."
            ):

                pages = load_knowledge(
                    pdf_paths=pdf_files,
                    text=pasted_text
                )

                chunks = chunk_text(
                    pages
                )

                vector_db = vector_storage(
                    chunks
                )

                st.session_state.vector_db = vector_db

                st.session_state.documents_loaded = True

                # Build quick summary
                summary_text = "\n\n".join(
                    chunk["content"]
                    for chunk in chunks[:5]
                )

                st.session_state.document_summary = (
                    summary_text[:1500]
                )

            st.success(
                f"Knowledge base ready! "
                f"Loaded {len(chunks)} chunks."
            )

        except Exception as e:

            st.error(
                f"Processing failed: {str(e)}"
            )

# ---------------------------------
# Display Chat History
# ---------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

# ---------------------------------
# Chat Input
# ---------------------------------

query = st.chat_input(
    "Ask a question..."
)

if query:

    if not st.session_state.documents_loaded:

        st.warning(
            "Please process documents first."
        )

    else:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": query
            }
        )

        with st.chat_message("user"):

            st.markdown(query)

        query_lower = (
            query.lower().strip()
        )

        small_talk = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening"
        ]

        summary_queries = [
            "summary",
            "summarize",
            "summarise",
            "what is the pdf about",
            "what is the document about",
            "what is this document about",
            "give me a summary"
        ]

        # ---------------------------------
        # Greetings
        # ---------------------------------

        if query_lower in small_talk:

            result = (
                "Hello! Ask me anything "
                "about the uploaded documents."
            )

        # ---------------------------------
        # Summary Questions
        # ---------------------------------

        elif query_lower in summary_queries:

            result = (
                st.session_state.document_summary
            )

        # ---------------------------------
        # RAG Pipeline
        # ---------------------------------

        else:

            retrieved_chunks = retriever(
                st.session_state.vector_db,
                query,
                k=5
            )

            result = answer(
                query,
                retrieved_chunks
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result
            }
        )

        with st.chat_message(
            "assistant"
        ):
            st.markdown(result)

