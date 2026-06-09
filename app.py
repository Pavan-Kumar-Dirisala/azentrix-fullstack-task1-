import tempfile
import streamlit as st

from rag.knowledge_loader import load_knowledge
from rag.chunker import chunk_text
from rag.vector_store import vector_storage
from rag.retriver import retriever
from rag.llm_answer import answer
from rag.llm_initializer import openai

# ---------------------------------
# Page Configuration
# ---------------------------------

st.set_page_config(
    page_title="DocMind — Document Q&A",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #F5F7FA !important;
    color: #1A1D23 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: #F5F7FA !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E4E7EC !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.25rem !important;
}

/* ── Sidebar logo area ── */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #E4E7EC;
}

.sidebar-brand-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6366F1, #818CF8);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}

.sidebar-brand-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1A1D23;
    letter-spacing: -0.02em;
}

.sidebar-brand-sub {
    font-size: 0.7rem;
    color: #9DA4AE;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Section labels ── */
.sidebar-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9DA4AE;
    margin: 1.25rem 0 0.6rem 0;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    width: 100%;
    margin-top: 0.75rem;
}

.status-pill.active {
    background: rgba(22, 163, 74, 0.08);
    color: #16A34A;
    border: 1px solid rgba(22, 163, 74, 0.2);
}

.status-pill.inactive {
    background: #F5F7FA;
    color: #9DA4AE;
    border: 1px solid #E4E7EC;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

.status-dot.active {
    background: #16A34A;
    box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.18);
    animation: pulse 2s ease-in-out infinite;
}

.status-dot.inactive {
    background: #D1D5DB;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.18); }
    50%       { box-shadow: 0 0 0 6px rgba(22, 163, 74, 0.05); }
}

/* ── Chunk stat badge ── */
.chunk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(99, 102, 241, 0.07);
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #6366F1;
    margin-top: 0.75rem;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #FAFBFC !important;
    border: 1px dashed #D1D5DB !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #6366F1 !important;
}

[data-testid="stFileUploader"] label {
    color: #6B7280 !important;
    font-size: 0.82rem !important;
}

/* ── Text area ── */
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    border: 1px solid #E4E7EC !important;
    border-radius: 10px !important;
    color: #1A1D23 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    resize: vertical !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #C0C6CF !important;
}

[data-testid="stTextArea"] label {
    color: #6B7280 !important;
    font-size: 0.8rem !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    height: 40px !important;
    border: none !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
}

/* Primary button */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #818CF8) !important;
    color: #fff !important;
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.25) !important;
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F52E0, #6366F1) !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.38) !important;
    transform: translateY(-1px) !important;
}

/* Secondary button */
[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #6B7280 !important;
    border: 1px solid #E4E7EC !important;
}

[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F5F7FA !important;
    color: #1A1D23 !important;
    border-color: #C0C6CF !important;
}

/* ── Main content area ── */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1100px !important;
}

/* ── Page header ── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #E4E7EC;
}

.page-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #1A1D23;
    letter-spacing: -0.03em;
    margin: 0 0 4px 0;
    line-height: 1.2;
}

.page-subtitle {
    font-size: 0.875rem;
    color: #6B7280;
    margin: 0;
    font-weight: 400;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    gap: 12px !important;
}

/* Avatar */
[data-testid="stChatMessage"] > div:first-child {
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* Message content wrapper */
[data-testid="stChatMessage"] > div:nth-child(2) {
    background: #FFFFFF !important;
    border: 1px solid #E4E7EC !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    max-width: 82% !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    color: #374151 !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
}

/* ── Chat input ── */
[data-testid="stChatInputContainer"] {
    background: #FFFFFF !important;
    border: 1px solid #E4E7EC !important;
    border-radius: 12px !important;
    padding: 0.25rem 0.5rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    color: #1A1D23 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #C0C6CF !important;
}

[data-testid="stChatInputContainer"] button {
    background: #6366F1 !important;
    border-radius: 8px !important;
    color: white !important;
    border: none !important;
}

[data-testid="stChatInputContainer"] button:hover {
    background: #4F52E0 !important;
}

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    gap: 1rem;
}

.empty-state-icon {
    width: 60px;
    height: 60px;
    background: #FFFFFF;
    border: 1px solid #E4E7EC;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.empty-state-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1A1D23;
    letter-spacing: -0.02em;
}

.empty-state-desc {
    font-size: 0.85rem;
    color: #9DA4AE;
    max-width: 320px;
    line-height: 1.5;
}

/* ── Summary card ── */
.summary-card {
    background: #FFFFFF;
    border: 1px solid #E4E7EC;
    border-left: 3px solid #6366F1;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.summary-card-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6366F1;
    margin-bottom: 0.5rem;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #E4E7EC !important;
    margin: 1.25rem 0 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.85rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {
    color: #6366F1 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E4E7EC;
    border-radius: 10px;
    padding: 0.875rem 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

[data-testid="stMetricLabel"] {
    color: #9DA4AE !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    color: #1A1D23 !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #9DA4AE; }

/* ── File uploader uploaded items ── */
[data-testid="stFileUploaderFile"] {
    background: #FAFBFC !important;
    border: 1px solid #E4E7EC !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    color: #6B7280 !important;
}

/* Hide streamlit default menu / footer ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

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

if "chunks" not in st.session_state:
    st.session_state.chunks = []

# ---------------------------------
# Sidebar
# ---------------------------------

with st.sidebar:

    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🧠</div>
        <div>
            <div class="sidebar-brand-text">DocMind</div>
            <div class="sidebar-brand-sub">RAG · Q&A Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Knowledge Source
    st.markdown('<div class="sidebar-section-label">Knowledge Source</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "PDF Files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files to build your knowledge base.",
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    pasted_text = st.text_area(
        "Or paste text directly",
        height=120,
        placeholder="Paste text here to include in the knowledge base…",
        label_visibility="visible"
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    process = st.button(
        "⚡ Build Knowledge Base",
        use_container_width=True,
        type="primary"
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    clear = st.button(
        "↩ Reset Session",
        use_container_width=True
    )

    # Status
    st.markdown('<div class="sidebar-section-label">Index Status</div>', unsafe_allow_html=True)

    if st.session_state.documents_loaded:
        st.markdown("""
        <div class="status-pill active">
            <div class="status-dot active"></div>
            Knowledge base active
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.chunks:
            st.markdown(
                f'<div class="chunk-badge">📦 {len(st.session_state.chunks)} chunks indexed</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown("""
        <div class="status-pill inactive">
            <div class="status-dot inactive"></div>
            Awaiting documents
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------
# Clear Session
# ---------------------------------

if clear:
    st.session_state.vector_db = None
    st.session_state.documents_loaded = False
    st.session_state.messages = []
    st.session_state.document_summary = ""
    st.session_state.chunks = []
    st.rerun()

# ---------------------------------
# Process Documents
# ---------------------------------

if process:
    if not uploaded_files and not pasted_text.strip():
        st.warning("Upload at least one PDF or paste some text to get started.")
    else:
        try:
            pdf_files = []
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    pdf_files.append({"path": tmp.name, "name": uploaded_file.name})

            with st.spinner("Reading documents…"):
                pages = load_knowledge(pdf_paths=pdf_files, text=pasted_text)

            with st.spinner("Splitting into chunks…"):
                chunks = chunk_text(pages)
                st.session_state.chunks = chunks

            with st.spinner("Building vector index…"):
                vector_db = vector_storage(chunks)
                st.session_state.vector_db = vector_db

            with st.spinner("Generating document summary…"):
                summary_context = "\n\n".join(
                    chunk["content"] for chunk in chunks[:5]
                )
                summary_response = openai.invoke(
                    f"Summarize the uploaded document(s) in 5 concise bullet points.\n\nContext:\n{summary_context}"
                )
                st.session_state.document_summary = summary_response.content

            st.session_state.documents_loaded = True
            st.toast(f"✅ Indexed {len(chunks)} chunks successfully.", icon="✅")
            st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")

# ---------------------------------
# Main Layout — Header
# ---------------------------------

col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    st.markdown("""
    <div class="page-header">
        <p class="page-title">Document Q&amp;A</p>
        <p class="page-subtitle">Ask questions about your documents in natural language. Answers are grounded in your uploaded content.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.session_state.documents_loaded:
        st.metric(
            label="Index",
            value="Ready",
            delta="Live",
        )
    else:
        st.metric(
            label="Index",
            value="Idle",
            delta="No docs",
            delta_color="inverse"
        )

# ---------------------------------
# Summary card (if loaded)
# ---------------------------------

if st.session_state.documents_loaded and st.session_state.document_summary:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-card-label">Document Summary</div>
        {st.session_state.document_summary.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------
# Chat History or Empty State
# ---------------------------------

chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        if st.session_state.documents_loaded:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">Knowledge base is ready</div>
                <div class="empty-state-desc">Start by asking a question below. You can ask for a summary, look up specific topics, or request full sections.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📄</div>
                <div class="empty-state-title">No documents loaded yet</div>
                <div class="empty-state-desc">Upload a PDF or paste text in the sidebar, then click <strong>Build Knowledge Base</strong> to get started.</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# ---------------------------------
# Chat Input
# ---------------------------------

query = st.chat_input("Ask anything about your documents…")

if query:
    if not st.session_state.documents_loaded:
        st.warning("Build the knowledge base first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        query_lower = query.lower().strip()

        small_talk = ["hi", "hello", "hey", "good morning", "good evening"]

        summary_queries = [
            "summary", "summarize", "summarise", "give me a summary",
            "document summary", "pdf summary", "overview", "document overview",
            "what is the pdf about", "what is the document about",
            "what is this document about"
        ]

        section_request_patterns = [
            "show all", "list all", "give all",
            "entire", "complete", "full", "whole"
        ]

        if query_lower in small_talk:
            result = "Hello! I'm ready to answer questions about your uploaded documents. What would you like to know?"

        elif query_lower in summary_queries:
            result = st.session_state.document_summary

        else:
            is_section_request = any(
                pattern in query_lower for pattern in section_request_patterns
            )
            retrieval_k = 20 if is_section_request else 5

            with st.spinner("Searching knowledge base…"):
                retrieved_chunks = retriever(
                    st.session_state.vector_db, query, k=retrieval_k
                )
                result = answer(query, retrieved_chunks)

        st.session_state.messages.append({"role": "assistant", "content": result})

        with st.chat_message("assistant"):
            st.markdown(result)