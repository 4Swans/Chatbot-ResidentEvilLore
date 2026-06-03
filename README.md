# Resident Evil Lore LLM RAG

Chatbot berbasis Retrieval-Augmented Generation (RAG) yang menggunakan data Lore Resident Evil, ChromaDB sebagai vector database, Google Gemini untuk embedding dan generative AI, serta Streamlit sebagai antarmuka web.

## Persyaratan Sistem

* Python 3.10 atau lebih baru
* Virtual Environment (venv)
* Koneksi internet
* Google Gemini API Key

---

## 1. Buka Terminal / Command Prompt

Buka terminal pilihan Anda (PowerShell atau Command Prompt) pada direktori proyek:

```bash
c:\Kuliah\Semester 8\Skripsi\Resident-Evil-Lore_LLM_RAG
```

---

## 2. Aktifkan Virtual Environment (venv)

Karena proyek sudah memiliki folder `venv`, cukup aktifkan environment tersebut.

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### Command Prompt (CMD)

```cmd
.\venv\Scripts\activate.bat
```

### Linux / macOS

```bash
source venv/bin/activate
```

Jika berhasil, terminal akan menampilkan awalan seperti berikut:

```bash
(venv)
```

---

## 3. Instal Dependensi

Pastikan seluruh library yang dibutuhkan telah terinstal dengan menjalankan:

```bash
pip install -r requirements.txt
```

---

## 4. Konfigurasi API Key

Aplikasi memerlukan API Key Gemini dari Google AI Studio untuk proses embedding dan menjawab pertanyaan.

File `.env` sudah tersedia dan berisi konfigurasi berikut:

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

Jika ingin menggunakan API Key milik sendiri, buka file `.env` dan ganti nilainya sesuai API Key yang dimiliki.

---

## 5. Ingestion Data (Opsional)

Langkah ini digunakan untuk:

* Membaca data cerita Resident Evil dari file JSON
* Melakukan text chunking
* Membuat embedding
* Menyimpan embedding ke ChromaDB

Jalankan perintah berikut:

```bash
python ingest.py
```

### Catatan

Folder `chroma_db` sudah tersedia pada proyek ini sehingga database kemungkinan telah terisi.

Langkah ini dapat dilewati jika:

* Database masih berfungsi dengan baik
* Tidak ada perubahan data sumber

Jalankan kembali `ingest.py` apabila:

* Menambahkan data baru
* Memperbarui data lore
* Database mengalami kerusakan atau error

---

## 6. Menjalankan Aplikasi Chatbot

Untuk menjalankan antarmuka chatbot berbasis Streamlit:

```bash
streamlit run app.py
```

---

## 7. Akses Aplikasi

Setelah aplikasi berjalan, Streamlit akan membuka browser secara otomatis.

Jika tidak terbuka otomatis, akses melalui alamat berikut:

```text
http://localhost:8501
```

---

## Fitur Utama

* Chatbot Lore Resident Evil
* Retrieval-Augmented Generation (RAG)
* ChromaDB Vector Database
* Google Gemini Embedding & LLM
* Pencarian informasi berbasis konteks
* Antarmuka web menggunakan Streamlit

---

## Struktur Proyek

```text
Resident-Evil-Lore_LLM_RAG/
│
├── app.py                 # Aplikasi Streamlit
├── ingest.py              # Proses ingestion data
├── requirements.txt       # Daftar dependensi
├── .env                   # API Key Gemini
├── chroma_db/             # Vector Database ChromaDB
├── data/                  # Dataset Lore Resident Evil
└── venv/                  # Virtual Environment
```

---

## Troubleshooting

### ModuleNotFoundError

Pastikan virtual environment telah aktif dan seluruh dependensi telah diinstal:

```bash
pip install -r requirements.txt
```

### Error API Key Gemini

Periksa file `.env` dan pastikan nilai `GOOGLE_API_KEY` valid.

### ChromaDB Tidak Ditemukan

Jalankan ulang proses ingestion:

```bash
python ingest.py
```

### Port Streamlit Sedang Digunakan

Jalankan Streamlit pada port lain:

```bash
streamlit run app.py --server.port 8502
```

---

## Penggunaan

1. Jalankan aplikasi Streamlit.
2. Buka halaman chatbot.
3. Ketik pertanyaan mengenai Lore Resident Evil.
4. Sistem akan mengambil informasi dari basis pengetahuan menggunakan RAG.
5. Gemini akan menghasilkan jawaban berdasarkan konteks yang ditemukan.

Selamat menggunakan Resident Evil Lore Chatbot.
