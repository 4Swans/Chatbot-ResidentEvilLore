"""
app.py - Streamlit Chatbot UI
===============================
Antarmuka chatbot RAG untuk Resident Evil Lore.
Jalankan: streamlit run app.py
"""

# --- SQLite Workaround untuk Streamlit Cloud ---
# Streamlit Cloud kadang menggunakan versi SQLite lama yang tidak kompatibel dengan ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# -----------------------------------------------

import streamlit as st
from rag_chain import query, get_collection_count

# ── Page Config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resident Evil Lore Chatbot",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header styling ── */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #dc2626, #991b1b, #7f1d1d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #a1a1aa;
        font-size: 0.95rem;
        margin: 0;
    }

    /* ── Divider ── */
    .header-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #dc2626, transparent);
        margin: 0.8rem 0 1.2rem 0;
        border: none;
    }

    /* ── Chat messages ── */
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 0.5rem !important;
    }

    /* ── Source badge ── */
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        color: #fecaca;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.15rem 0.2rem;
        border: 1px solid #dc262644;
    }

    /* ── Sidebar ── */
    .sidebar-stat {
        background: linear-gradient(135deg, #1c1917, #292524);
        border: 1px solid #44403c;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        text-align: center;
    }
    .sidebar-stat .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #dc2626;
    }
    .sidebar-stat .stat-label {
        font-size: 0.8rem;
        color: #a8a29e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ── Suggestion chips ── */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧬 Resident Evil Lore Chatbot</h1>
    <p>Tanyakan apapun tentang cerita & lore Resident Evil — Powered by RAG + Gemini AI</p>
</div>
<div class="header-divider"></div>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Tentang")
    st.markdown(
        "Chatbot ini menggunakan **Retrieval-Augmented Generation (RAG)** "
        "untuk menjawab pertanyaan seputar lore Resident Evil berdasarkan "
        "database cerita yang sudah diindeks."
    )

    st.markdown("---")

    # Statistik database
    doc_count = get_collection_count()
    st.markdown(f"""
    <div class="sidebar-stat">
        <div class="stat-number">{doc_count}</div>
        <div class="stat-label">Chunks di Database</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### ⚙️ Teknologi")
    st.markdown("""
    - 🤖 **LLM**: Gemini 2.5 Flash
    - 🗄️ **Vector DB**: ChromaDB
    - 🔤 **Embedding**: text-embedding-004
    - 🖥️ **UI**: Streamlit
    """)

    st.markdown("---")

    # Tombol clear chat
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Session State ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Tampilkan history chat ──────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧟" if message["role"] == "assistant" else "🧑"):
        st.markdown(message["content"])

        # Tampilkan sumber jika ada
        if message.get("sources"):
            sources_html = "".join(
                f'<span class="source-badge">📖 {src["game"]}</span>'
                for src in message["sources"]
            )
            st.markdown(f"<div style='margin-top: 0.5rem;'>{sources_html}</div>", unsafe_allow_html=True)

# ── Suggestion chips jika belum ada chat ────────────────────────────────
if not st.session_state.messages:
    st.markdown("#### 💡 Coba tanyakan:")
    suggestions = [
        "Siapa Albert Wesker?",
        "Apa itu T-Virus?",
        "Ceritakan tentang Raccoon City",
        "Siapa Leon Kennedy?",
        "Apa yang terjadi di Resident Evil 4?",
        "Siapa Jill Valentine?",
    ]

    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

# ── Chat input ──────────────────────────────────────────────────────────
# Cek apakah ada pending question dari suggestion
prompt = None
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

# Input box
user_input = st.chat_input("Tanyakan seputar lore Resident Evil...")

if user_input:
    prompt = user_input

if prompt:
    # Tampilkan pesan user
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate jawaban
    with st.chat_message("assistant", avatar="🧟"):
        with st.spinner("🔍 Mencari di database lore..."):
            try:
                result = query(prompt)
                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                # Tampilkan sumber
                if sources:
                    sources_html = "".join(
                        f'<span class="source-badge">📖 {src["game"]}</span>'
                        for src in sources
                    )
                    st.markdown(
                        f"<div style='margin-top: 0.5rem;'>{sources_html}</div>",
                        unsafe_allow_html=True,
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except Exception as e:
                error_msg = f"❌ Terjadi error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })
