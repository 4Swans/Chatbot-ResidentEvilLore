"""
show_chromadb.py - Menampilkan isi ChromaDB untuk keperluan dokumentasi/screenshot
"""

import os
import chromadb

# Resolve path relatif ke root proyek (satu level di atas folder Testing)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(ROOT_DIR, "chroma_db")
COLLECTION_NAME = "resident_evil_lore"

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

# -- Ringkasan Database --------------------------------------------------
total = collection.count()
print("=" * 70)
print(" CHROMADB - VECTOR DATABASE CONTENTS")
print("=" * 70)
print(f"  Collection    : {COLLECTION_NAME}")
print(f"  Persist Dir   : {CHROMA_DIR}")
print(f"  Total Vectors : {total}")
print("=" * 70)

# -- Ambil semua data -----------------------------------------------------
results = collection.get(
    include=["documents", "metadatas", "embeddings"],
    limit=3,  # Tampilkan 10 data pertama (ubah jika perlu)
)

# -- Tampilkan data per entry ---------------------------------------------
for i in range(len(results["ids"])):
    print(f"\n{'-' * 70}")
    print(f"  ID        : {results['ids'][i]}")
    print(f"  Source     : {results['metadatas'][i].get('source', 'N/A')}")
    print(f"  Paragraph : {results['metadatas'][i].get('paragraph_index', 'N/A')}")

    # Tampilkan teks (potong jika terlalu panjang)
    text = results["documents"][i]
    if len(text) > 200:
        text_display = text[:200] + "..."
    else:
        text_display = text
    print(f"  Text      : {text_display}")

    # Tampilkan sebagian embedding vector (5 dimensi pertama)
    if results["embeddings"] is not None and len(results["embeddings"]) > i:
        emb = results["embeddings"][i]
        emb_preview = [round(v, 6) for v in emb[:5]]
        print(f"  Embedding : {emb_preview}... ({len(emb)} dimensi)")

print(f"\n{'-' * 70}")
print(f"\n  Menampilkan {len(results['ids'])} dari {total} total vectors.")

