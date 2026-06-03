"""
rag_chain.py - RAG Query Engine
================================
Module untuk melakukan Retrieval-Augmented Generation.
Mengambil konteks relevan dari ChromaDB dan mengirim ke Gemini 2.5 Flash.
"""

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ── Load environment variables ──────────────────────────────────────────
load_dotenv()

# ── Konfigurasi ─────────────────────────────────────────────────────────
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "resident_evil_lore"
TOP_K = 5  # Jumlah dokumen relevan yang diambil

# ── Prompt Template ─────────────────────────────────────────────────────
RAG_PROMPT_TEMPLATE = """Kamu adalah seorang ahli lore Resident Evil yang sangat berpengetahuan.
Jawab pertanyaan pengguna HANYA berdasarkan konteks yang diberikan di bawah ini.
Jika informasi tidak ditemukan dalam konteks, katakan dengan jujur bahwa kamu tidak menemukan informasinya dalam database lore yang tersedia.

Berikan jawaban yang detail, informatif, dan menarik. Gunakan bahasa Indonesia yang baik.
Jika relevan, sebutkan dari game mana informasi tersebut berasal.

KONTEKS:
{context}

PERTANYAAN: {question}

JAWABAN:"""


def get_vectorstore() -> Chroma:
    """Membuka koneksi ke ChromaDB yang sudah ada."""
    embedding_function = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME,
    )

    return vectorstore


def get_retriever(top_k: int = TOP_K):
    """Membuat retriever dari ChromaDB vectorstore."""
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
    return retriever


def format_docs(docs) -> str:
    """Format retrieved documents menjadi string konteks."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        formatted.append(f"[Sumber: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def get_rag_chain():
    """Membuat RAG chain lengkap: retriever → prompt → LLM → output."""
    retriever = get_retriever()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def query(question: str) -> dict:
    """
    Menjalankan RAG query dan mengembalikan jawaban beserta sumber.

    Returns:
        dict: {"answer": str, "sources": list[dict]}
    """
    retriever = get_retriever()
    docs = retriever.invoke(question)

    # Format context
    context = format_docs(docs)

    # LLM call
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({"context": context, "question": question})

    # Kumpulkan sumber unik
    sources = []
    seen = set()
    for doc in docs:
        src = doc.metadata.get("source", "Unknown")
        if src not in seen:
            seen.add(src)
            sources.append({
                "game": src,
                "snippet": doc.page_content[:150] + "...",
            })

    return {
        "answer": answer,
        "sources": sources,
    }


def get_collection_count() -> int:
    """Mengembalikan jumlah dokumen di ChromaDB."""
    try:
        vectorstore = get_vectorstore()
        return vectorstore._collection.count()
    except Exception:
        return 0


# ── Test manual ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔍 Testing RAG Query Engine...\n")
    test_question = "Siapa Albert Wesker dan apa motivasinya?"
    result = query(test_question)

    print(f"❓ Pertanyaan: {test_question}")
    print(f"\n💬 Jawaban:\n{result['answer']}")
    print(f"\n📚 Sumber:")
    for src in result["sources"]:
        print(f"   - {src['game']}: {src['snippet']}")
