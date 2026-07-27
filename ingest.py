"""
ingest.py - Data Ingestion Pipeline
=====================================
Membaca data JSON Resident Evil lore, melakukan chunking,
embedding via Gemini, dan menyimpan ke ChromaDB.

"""

import json
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ── Load environment variables ──────────────────────────────────────────
load_dotenv()

# ── Konfigurasi ─────────────────────────────────────────────────────────
DATA_PATH = os.path.join("Data", "resident_evil_story.json")
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "resident_evil_lore"

# Chunk size 1000 karakter, overlap 200 karakter
# Alasan: paragraf dalam JSON bervariasi 200-2000 karakter.
# Dengan ukuran 1000, paragraf pendek-menengah (~200-800 char) tetap utuh,
# sedangkan paragraf panjang (>1000 char) akan dipecah dengan overlap
# yang cukup untuk menjaga konteks antar chunk.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_json_data(file_path: str) -> list[Document]:
    """
    Membaca file JSON dan mengubahnya menjadi list of LangChain Documents.
    Setiap paragraf menjadi satu Document dengan metadata berisi judul game.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for entry in data:
        title = entry["title"]
        for i, paragraph in enumerate(entry["data"]):
            doc = Document(
                page_content=paragraph,
                metadata={
                    "source": title,
                    "paragraph_index": i,
                },
            )
            documents.append(doc)

    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Melakukan chunking pada dokumen menggunakan RecursiveCharacterTextSplitter.
    Mempertahankan metadata dari dokumen asli.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)
    return chunks


def create_embeddings_and_store(chunks: list[Document]) -> Chroma:
    """
    Membuat embedding dari chunks menggunakan Gemini embedding
    dan menyimpannya ke ChromaDB secara persistent.
    Menggunakan batching kecil + retry untuk menghindari rate limit.
    """
    import time

    embedding_function = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    # Hapus data lama jika ada
    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print("   🗑️  Database lama dihapus.")

    # Buat ChromaDB
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME,
    )

    # Batch size sangat kecil agar aman dari rate limit
    # Free tier: 100 embed requests per menit
    BATCH_SIZE = 10
    MAX_RETRIES = 3
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        print(f"    Batch {batch_num}/{total_batches}: embedding {len(batch)} chunks...")

        texts = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]

        # Retry loop untuk handle rate limit
        for attempt in range(MAX_RETRIES):
            try:
                vectorstore.add_texts(texts=texts, metadatas=metadatas)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = 65 * (attempt + 1)
                    print(f"   Rate limit hit, menunggu {wait}s (attempt {attempt+1}/{MAX_RETRIES})...")
                    time.sleep(wait)
                else:
                    raise e
        else:
            print(f"    Batch {batch_num} gagal setelah {MAX_RETRIES} percobaan!")
            raise RuntimeError(f"Batch {batch_num} failed after {MAX_RETRIES} retries")

        # Delay antar batch untuk menghindari rate limit
        if i + BATCH_SIZE < len(chunks):
            print(f"    Delay 5s antar batch...")
            time.sleep(5)

    return vectorstore


def main():
    print("=" * 60)
    print(" RESIDENT EVIL LORE - DATA INGESTION PIPELINE")
    print("=" * 60)

    # 1. Load data JSON
    print("\n [1/3] Memuat data JSON...")
    documents = load_json_data(DATA_PATH)
    print(f"    {len(documents)} paragraf dimuat dari {DATA_PATH}")

    # Tampilkan statistik per game
    game_counts = {}
    for doc in documents:
        src = doc.metadata["source"]
        game_counts[src] = game_counts.get(src, 0) + 1
    for game, count in game_counts.items():
        print(f" {game}: {count} paragraf")

    # 2. Chunking
    print(f"\n  [2/3] Melakukan chunking (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = chunk_documents(documents)
    print(f"   {len(chunks)} chunks dihasilkan dari {len(documents)} paragraf")

    # Statistik chunk
    chunk_lengths = [len(c.page_content) for c in chunks]
    print(f"      Rata-rata panjang chunk: {sum(chunk_lengths) // len(chunk_lengths)} karakter")
    print(f"      Chunk terpendek: {min(chunk_lengths)} karakter")
    print(f"      Chunk terpanjang: {max(chunk_lengths)} karakter")

    # 3. Embedding & Store ke ChromaDB
    print("\n🔮 [3/3] Membuat embedding dan menyimpan ke ChromaDB...")
    vectorstore = create_embeddings_and_store(chunks)
    count = vectorstore._collection.count()
    print(f"    {count} vectors tersimpan di ChromaDB ({CHROMA_DIR})")

    print("\n" + "=" * 60)
    print("INGESTION SELESAI! Database siap digunakan.")
    print("=" * 60)


if __name__ == "__main__":
    main()
