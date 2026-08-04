Misalkan sebelumnya kita sudah memiliki:

```text id="6c2l3x"
project/
├── models/
│   ├── bge-m3-q8_0.gguf
│   └── llama-3.gguf
│
├── chunks/
├── chroma_db/
└── query.py
```

Dan seluruh embedding dibuat menggunakan **llama.cpp + ChromaDB**.

---

# Alur Retrieval

```text id="3r1m7n"
Pertanyaan User
│
├── "Bagaimana cara menginstal aplikasi?"
│
├── llama.cpp (embedding model)
│   └── [0.41, -0.82, ...]
│
├── ChromaDB
│   └── Similarity Search (Top-K)
│
└── Hasil
    ├── chunk_001
    ├── chunk_015
    └── chunk_023
```

---

# Script Sederhana: `query.py`

```python
from chromadb import PersistentClient
from llama_cpp import Llama


# =====================================
# Konfigurasi
# =====================================
EMBED_MODEL = "models/bge-m3-q8_0.gguf"
DB_DIR = "chroma_db"
COLLECTION_NAME = "knowledge"
TOP_K = 3


# =====================================
# Inisialisasi Embedding Model
# =====================================
embedder = Llama(
    model_path=EMBED_MODEL,
    embedding=True,
    verbose=False,
)


# =====================================
# Hubungkan ke ChromaDB
# =====================================
client = PersistentClient(path=DB_DIR)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# =====================================
# Input Pertanyaan
# =====================================
question = input("Pertanyaan: ")


# =====================================
# Buat Embedding Pertanyaan
# =====================================
query_embedding = embedder.embed(question)


# =====================================
# Cari Chunk yang Mirip
# =====================================
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=TOP_K,
)


# =====================================
# Tampilkan Hasil
# =====================================
print("\n=== HASIL PENCARIAN ===\n")

for i in range(len(results["ids"][0])):

    chunk_id = results["ids"][0][i]
    document = results["documents"][0][i]
    metadata = results["metadatas"][0][i]
    distance = results["distances"][0][i]

    print(f"[{i+1}] {chunk_id}")
    print(f"Source   : {metadata['source']}")
    print(f"Distance : {distance}")
    print(document)
    print("-" * 60)
```

---

# Contoh Output

```text id="u4h3bo"
$ python query.py

Pertanyaan:
Bagaimana cara menginstal aplikasi?


=== HASIL PENCARIAN ===

[1] chunk_001
Source   : chunk_001.txt
Distance : 0.034

Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi

------------------------------------------------------------

[2] chunk_015
Source   : chunk_015.txt
Distance : 0.081

Pastikan koneksi internet aktif sebelum instalasi.

------------------------------------------------------------

[3] chunk_023
Source   : chunk_023.txt
Distance : 0.102

Jika paket tidak ditemukan, lakukan sinkronisasi repository.

------------------------------------------------------------
```

---

# Mengubah Hasil Retrieval Menjadi Context untuk LLM

Biasanya hasil pencarian digabung menjadi satu string:

```python
context = "\n\n".join(results["documents"][0])
```

Hasil:

```text id="2m0a6h"
Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi


Pastikan koneksi internet aktif sebelum instalasi.


Jika paket tidak ditemukan, lakukan sinkronisasi repository.
```

---

# Alur Lengkap Retrieval

```text id="b5h2ls"
User:
"Bagaimana cara menginstal aplikasi?"
│
├── llama.cpp (embedding model)
│   └── query vector
│
├── ChromaDB
│   ├── bandingkan dengan seluruh vector
│   ├── urutkan berdasarkan kemiripan
│   └── ambil Top-3
│
└── Hasil
    ├── chunk_001
    ├── chunk_015
    └── chunk_023
```

---

# Langkah Berikutnya: RAG Penuh

Setelah mendapatkan chunk yang relevan:

```text id="z8k4yq"
Pertanyaan User
│
├── Embedding Pertanyaan
│
├── ChromaDB
│
├── Top-K Chunk
│
├── Gabungkan menjadi Context
│
├── Prompt Builder
│
└── llama.cpp (chat model)
    │
    └── Jawaban AI
```

Contoh sederhana:

```python
prompt = f"""
Jawablah berdasarkan konteks berikut.

KONTEKS:
{context}

PERTANYAAN:
{question}
"""
```

Lalu dikirim ke model chat GGUF menggunakan `Llama(..., chat_format=...)` atau `llama-cli`. Dengan demikian, pipeline RAG lengkap telah terbentuk.
