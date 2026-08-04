Jika diasumsikan **folder `chunks/` sudah berisi file hasil chunking** (1 file = 1 chunk), maka script embedding sederhananya seperti ini:

Struktur folder:

```text
project/
├── chunks/
│   ├── chunk_0001.txt
│   ├── chunk_0002.txt
│   └── chunk_0003.txt
│
├── chroma_db/
└── embed.py
```

Alurnya:

```text
chunks/
│
├── chunk_0001.txt
│   └── Dibaca Python
│       └── Dibuat embedding
│           └── Disimpan ke ChromaDB
│
├── chunk_0002.txt
│   └── Dibaca Python
│       └── Dibuat embedding
│           └── Disimpan ke ChromaDB
│
└── chunk_0003.txt
    └── Dibaca Python
        └── Dibuat embedding
            └── Disimpan ke ChromaDB
```

Script Python:

```python
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ==========================
# Konfigurasi
# ==========================
CHUNK_DIR = "chunks"
DB_DIR = "chroma_db"
COLLECTION_NAME = "knowledge"

EMBED_MODEL = "BAAI/bge-m3"


# ==========================
# Inisialisasi
# ==========================
model = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(path=DB_DIR)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ==========================
# Proses Embedding
# ==========================
for file in sorted(Path(CHUNK_DIR).glob("*.txt")):

    # 1. Baca isi chunk
    text = file.read_text(encoding="utf-8").strip()

    if not text:
        continue

    # 2. Buat embedding
    embedding = model.encode(text).tolist()

    # 3. Simpan ke ChromaDB
    collection.add(
        ids=[file.stem],              # chunk_0001
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "source": file.name
            }
        ]
    )

    print(f"✓ {file.name}")


print("\nEmbedding selesai.")
```

Install dependensi:

```bash
pip install chromadb sentence-transformers
```

---

## Analogi langkah per langkah

```text
chunk_0001.txt
│
├── Python membaca file
│
├── "Llama.cpp adalah framework inferensi..."
│
├── Model embedding mengubah teks menjadi:
│   [0.12, -0.45, 0.88, ...]
│
├── Metadata dibuat:
│   source = chunk_0001.txt
│
└── Disimpan ke ChromaDB
    │
    └── knowledge
        │
        └── id = chunk_0001
```

Setelah seluruh proses selesai, isi database secara logis menjadi:

```text
ChromaDB
└── Collection: knowledge
    │
    ├── chunk_0001
    │   ├── document
    │   ├── embedding
    │   └── metadata
    │
    ├── chunk_0002
    │   ├── document
    │   ├── embedding
    │   └── metadata
    │
    └── chunk_0003
        ├── document
        ├── embedding
        └── metadata
```

Jika menggunakan **llama.cpp sepenuhnya tanpa `sentence-transformers`**, alurnya sedikit berubah:

```text
chunk_0001.txt
    │
    └── llama-embedding
            │
            └── vector
                    │
                    └── ChromaDB
```

Misalnya memakai model embedding `.gguf` seperti `bge-m3-q8_0.gguf` melalui `llama-server --embedding` atau `llama-cpp-python`, sehingga seluruh pipeline tetap berada dalam ekosistem llama.cpp.
