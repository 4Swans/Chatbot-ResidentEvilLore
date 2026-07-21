"""
show_retrieval.py
Script untuk menampilkan hasil retrieval chunk dari ChromaDB ke terminal.
Digunakan hanya untuk keperluan dokumentasi / penulisan skripsi.
"""

from rag_chain import get_retriever
from dotenv import load_dotenv

load_dotenv()

# ── Ganti pertanyaan di sini ──────────────────────────────────────────────
QUESTION = "Siapa Albert Wesker dan apa motivasinya?"
# ─────────────────────────────────────────────────────────────────────────

def show_retrieval(question: str):
    print("=" * 70)
    print(f"  HASIL RETRIEVAL")
    print(f"  Pertanyaan : {question}")
    print("=" * 70)

    retriever = get_retriever()
    docs = retriever.invoke(question)

    print(f"\n  Total chunk yang diambil : {len(docs)}\n")

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        idx    = doc.metadata.get("paragraph_index", "-")
        print(f"  {'-' * 66}")
        print(f"  Chunk #{i}")
        print(f"  Sumber          : {source}")
        print(f"  Paragraph Index : {idx}")
        print(f"  Panjang         : {len(doc.page_content)} karakter")
        print(f"  {'-' * 66}")
        print(f"  {doc.page_content}")
        print()

    print("=" * 70)

if __name__ == "__main__":
    show_retrieval(QUESTION)
