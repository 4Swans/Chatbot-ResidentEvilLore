"""
test_rag.py - Script Pengujian RAG System
==========================================
Menjalankan serangkaian pertanyaan uji terhadap sistem RAG,
mencatat jawaban, sumber, dan statistik, lalu menyimpan ke file TXT.

Jalankan: python test_rag.py
"""

import os
import sys
import time
from datetime import datetime

# Fix encoding untuk Windows
sys.stdout.reconfigure(encoding='utf-8')

# Tambahkan root proyek ke sys.path agar bisa import rag_chain & ingest
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv

load_dotenv()

# ── Import modul RAG ────────────────────────────────────────────────────
from rag_chain import query, get_collection_count, get_retriever
from ingest import load_json_data, chunk_documents, DATA_PATH

# ── Daftar Pertanyaan Uji ───────────────────────────────────────────────
TEST_QUESTIONS = [
    # Kategori 1: Karakter
    {
        "kategori": "Karakter",
        "no": 1,
        "pertanyaan": "Siapa Albert Wesker dan apa motivasinya?",
    },
    {
        "kategori": "Karakter",
        "no": 2,
        "pertanyaan": "Siapa Leon Kennedy dan bagaimana perannya dalam seri Resident Evil?",
    },
    {
        "kategori": "Karakter",
        "no": 3,
        "pertanyaan": "Siapa Jill Valentine?",
    },
    # Kategori 2: Virus/Parasit
    {
        "kategori": "Virus/Parasit",
        "no": 4,
        "pertanyaan": "Apa itu T-Virus dan bagaimana asal-usulnya?",
    },
    {
        "kategori": "Virus/Parasit",
        "no": 5,
        "pertanyaan": "Apa perbedaan antara T-Virus dan G-Virus?",
    },
    {
        "kategori": "Virus/Parasit",
        "no": 6,
        "pertanyaan": "Apa itu Las Plagas?",
    },
    # Kategori 3: Lokasi/Event
    {
        "kategori": "Lokasi/Event",
        "no": 7,
        "pertanyaan": "Ceritakan tentang insiden Raccoon City",
    },
    {
        "kategori": "Lokasi/Event",
        "no": 8,
        "pertanyaan": "Apa yang terjadi di Spencer Mansion?",
    },
    # Kategori 4: Alur Cerita Spesifik
    {
        "kategori": "Alur Cerita",
        "no": 9,
        "pertanyaan": "Apa yang terjadi di Resident Evil 4?",
    },
    {
        "kategori": "Alur Cerita",
        "no": 10,
        "pertanyaan": "Ceritakan alur cerita Resident Evil 0",
    },
    # Kategori 5: Hubungan Antar Karakter
    {
        "kategori": "Hubungan Karakter",
        "no": 11,
        "pertanyaan": "Apa hubungan antara Chris Redfield dan Claire Redfield?",
    },
    {
        "kategori": "Hubungan Karakter",
        "no": 12,
        "pertanyaan": "Bagaimana hubungan antara William Birkin dan Albert Wesker?",
    },
    # Kategori 6: Pertanyaan Lintas-Seri
    {
        "kategori": "Lintas-Seri",
        "no": 13,
        "pertanyaan": "Bagaimana Umbrella Corporation akhirnya dihancurkan?",
    },
    {
        "kategori": "Lintas-Seri",
        "no": 14,
        "pertanyaan": "Apa itu B.S.A.A. dan siapa saja anggotanya?",
    },
    # Kategori 7: Organisasi
    {
        "kategori": "Organisasi",
        "no": 15,
        "pertanyaan": "Apa itu Umbrella Corporation dan apa tujuan sebenarnya?",
    },
    # Kategori 8: Pertanyaan di Luar Konteks
    {
        "kategori": "Di Luar Konteks",
        "no": 16,
        "pertanyaan": "Siapa karakter utama di Final Fantasy VII?",
    },
    {
        "kategori": "Di Luar Konteks",
        "no": 17,
        "pertanyaan": "Bagaimana cara memasak nasi goreng?",
    },
    # Kategori 9: Pertanyaan Detail/Spesifik
    {
        "kategori": "Detail Spesifik",
        "no": 18,
        "pertanyaan": "Siapa Nemesis dan mengapa dia mengejar Jill?",
    },
    {
        "kategori": "Detail Spesifik",
        "no": 19,
        "pertanyaan": "Apa yang terjadi pada Sherry Birkin di Resident Evil 2?",
    },
    {
        "kategori": "Detail Spesifik",
        "no": 20,
        "pertanyaan": "Siapa Queen Leech dan apa hubungannya dengan Dr. Marcus?",
    },
]


def get_dataset_stats():
    """Mengumpulkan statistik dataset."""
    documents = load_json_data(DATA_PATH)
    chunks = chunk_documents(documents)
    
    # Statistik per game
    game_counts = {}
    for doc in documents:
        src = doc.metadata["source"]
        game_counts[src] = game_counts.get(src, 0) + 1

    # Statistik chunk
    chunk_lengths = [len(c.page_content) for c in chunks]
    chunk_per_game = {}
    for c in chunks:
        src = c.metadata["source"]
        chunk_per_game[src] = chunk_per_game.get(src, 0) + 1

    return {
        "total_paragraf": len(documents),
        "total_chunks": len(chunks),
        "game_counts": game_counts,
        "chunk_per_game": chunk_per_game,
        "avg_chunk_len": sum(chunk_lengths) // len(chunk_lengths),
        "min_chunk_len": min(chunk_lengths),
        "max_chunk_len": max(chunk_lengths),
        "db_count": get_collection_count(),
    }


def run_tests():
    """Menjalankan seluruh pengujian dan mengembalikan hasil."""
    results = []
    
    for test in TEST_QUESTIONS:
        no = test["no"]
        kategori = test["kategori"]
        pertanyaan = test["pertanyaan"]
        
        print(f"  [{no:2d}/20] [{kategori}] {pertanyaan[:50]}...")
        
        start_time = time.time()
        try:
            result = query(pertanyaan)
            elapsed = time.time() - start_time
            
            results.append({
                "no": no,
                "kategori": kategori,
                "pertanyaan": pertanyaan,
                "jawaban": result["answer"],
                "sources": result["sources"],
                "waktu": round(elapsed, 2),
                "status": "OK",
            })
            print(f"         -> OK ({elapsed:.2f}s, {len(result['sources'])} sumber)")
        except Exception as e:
            elapsed = time.time() - start_time
            results.append({
                "no": no,
                "kategori": kategori,
                "pertanyaan": pertanyaan,
                "jawaban": f"ERROR: {str(e)}",
                "sources": [],
                "waktu": round(elapsed, 2),
                "status": "ERROR",
            })
            print(f"         -> ERROR ({str(e)[:60]})")
        
        # Delay antar query untuk menghindari rate limit
        time.sleep(2)
    
    return results


def save_results(stats, results, filepath):
    """Menyimpan hasil pengujian ke file TXT."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  HASIL PENGUJIAN SISTEM RAG - RESIDENT EVIL LORE CHATBOT\n")
        f.write(f"  Tanggal Pengujian: {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        
        # ── Statistik Dataset ───────────────────────────────────────────
        f.write("-" * 80 + "\n")
        f.write("  BAGIAN 1: STATISTIK DATASET DAN PERSIAPAN DATA\n")
        f.write("-" * 80 + "\n\n")
        
        f.write(f"  Total Paragraf Asli    : {stats['total_paragraf']}\n")
        f.write(f"  Total Chunks           : {stats['total_chunks']}\n")
        f.write(f"  Vektor di ChromaDB     : {stats['db_count']}\n")
        f.write(f"  Rata-rata Panjang Chunk : {stats['avg_chunk_len']} karakter\n")
        f.write(f"  Chunk Terpendek        : {stats['min_chunk_len']} karakter\n")
        f.write(f"  Chunk Terpanjang       : {stats['max_chunk_len']} karakter\n")
        f.write("\n")
        
        f.write("  Distribusi Paragraf per Game:\n")
        for game, count in stats["game_counts"].items():
            f.write(f"    - {game}: {count} paragraf\n")
        f.write("\n")
        
        f.write("  Distribusi Chunk per Game:\n")
        for game, count in stats["chunk_per_game"].items():
            f.write(f"    - {game}: {count} chunks\n")
        f.write("\n\n")
        
        # ── Hasil Pengujian ─────────────────────────────────────────────
        f.write("-" * 80 + "\n")
        f.write("  BAGIAN 2: HASIL PENGUJIAN KUALITAS JAWABAN\n")
        f.write("-" * 80 + "\n\n")
        
        for r in results:
            f.write(f"{'=' * 80}\n")
            f.write(f"  Pertanyaan #{r['no']} [{r['kategori']}]\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"  PERTANYAAN : {r['pertanyaan']}\n")
            f.write(f"  STATUS     : {r['status']}\n")
            f.write(f"  WAKTU      : {r['waktu']} detik\n")
            f.write(f"  SUMBER     : {', '.join([s['game'] for s in r['sources']]) if r['sources'] else 'Tidak ada'}\n")
            f.write(f"\n  JAWABAN:\n")
            f.write(f"  {'-' * 70}\n")
            # Indent jawaban
            for line in r["jawaban"].split("\n"):
                f.write(f"  {line}\n")
            f.write(f"  {'-' * 70}\n\n")
        
        # ── Ringkasan ──────────────────────────────────────────────────
        f.write("\n" + "-" * 80 + "\n")
        f.write("  BAGIAN 3: RINGKASAN HASIL PENGUJIAN\n")
        f.write("-" * 80 + "\n\n")
        
        total = len(results)
        ok_count = sum(1 for r in results if r["status"] == "OK")
        err_count = total - ok_count
        avg_time = sum(r["waktu"] for r in results) / total if total > 0 else 0
        
        f.write(f"  Total Pertanyaan Uji   : {total}\n")
        f.write(f"  Berhasil (OK)          : {ok_count}\n")
        f.write(f"  Gagal (ERROR)          : {err_count}\n")
        f.write(f"  Tingkat Keberhasilan   : {ok_count/total*100:.1f}%\n")
        f.write(f"  Rata-rata Waktu Respon : {avg_time:.2f} detik\n")
        f.write("\n")
        
        # Ringkasan per kategori
        f.write("  Ringkasan per Kategori:\n")
        categories = {}
        for r in results:
            cat = r["kategori"]
            if cat not in categories:
                categories[cat] = {"total": 0, "ok": 0, "times": []}
            categories[cat]["total"] += 1
            if r["status"] == "OK":
                categories[cat]["ok"] += 1
            categories[cat]["times"].append(r["waktu"])
        
        for cat, data in categories.items():
            avg_t = sum(data["times"]) / len(data["times"])
            f.write(f"    - {cat}: {data['ok']}/{data['total']} berhasil, avg {avg_t:.2f}s\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("  AKHIR LAPORAN PENGUJIAN\n")
        f.write("=" * 80 + "\n")
    
    return filepath


def main():
    print("=" * 60)
    print("  PENGUJIAN SISTEM RAG - RESIDENT EVIL LORE CHATBOT")
    print("=" * 60)
    
    # 1. Kumpulkan statistik dataset
    print("\n📊 [1/3] Mengumpulkan statistik dataset...")
    stats = get_dataset_stats()
    print(f"   Total paragraf: {stats['total_paragraf']}")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Vektor di DB: {stats['db_count']}")
    
    # 2. Jalankan pengujian
    print(f"\n🧪 [2/3] Menjalankan {len(TEST_QUESTIONS)} pertanyaan uji...")
    results = run_tests()
    
    # 3. Simpan hasil
    print("\n💾 [3/3] Menyimpan hasil pengujian...")
    output_file = os.path.join(ROOT_DIR, "Data", "hasil_pengujian_rag.txt")
    save_results(stats, results, output_file)
    print(f"   Hasil disimpan di: {output_file}")
    
    # Ringkasan
    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\n✅ Selesai! {ok}/{len(results)} pertanyaan berhasil dijawab.")
    print("=" * 60)


if __name__ == "__main__":
    main()
