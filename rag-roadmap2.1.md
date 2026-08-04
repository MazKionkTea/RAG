Berikut contoh paling sederhana jika seluruh proses embedding menggunakan **llama.cpp** melalui library `llama-cpp-python` dan model embedding `.gguf`.

Struktur folder:

```text
project/
├── models/
│   └── bge-m3-q8_0.gguf
│
├── chunks/
│   ├── chunk_0001.txt
│   ├── chunk_0002.txt
│   └── chunk_0003.txt
│
├── chroma_db/
└── embed.py
```

Alur:

```text
chunks/
│
├── chunk_0001.txt
│   └── llama.cpp embedding
│       └── vector
│           └── ChromaDB
│
├── chunk_0002.txt
│   └── llama.cpp embedding
│       └── vector
│           └── ChromaDB
│
└── chunk_0003.txt
    └── llama.cpp embedding
        └── vector
            └── ChromaDB
```

Script `embed.py`:

```python
from pathlib import Path

import chromadb
from llama_cpp import Llama


# =====================================
# Konfigurasi
# =====================================
MODEL_PATH = "models/bge-m3-q8_0.gguf"

CHUNK_DIR = "chunks"
DB_DIR = "chroma_db"
COLLECTION_NAME = "knowledge"


# =====================================
# Inisialisasi llama.cpp (embedding)
# =====================================
llm = Llama(
    model_path=MODEL_PATH,
    embedding=True,
    n_ctx=2048,
    verbose=False,
)


# =====================================
# Inisialisasi ChromaDB
# =====================================
client = chromadb.PersistentClient(path=DB_DIR)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# =====================================
# Proses Embedding
# =====================================
for file in sorted(Path(CHUNK_DIR).glob("*.txt")):

    text = file.read_text(
        encoding="utf-8"
    ).strip()

    if not text:
        continue

    # Buat embedding menggunakan llama.cpp
    embedding = llm.embed(text)

    # Simpan ke ChromaDB
    collection.add(
        ids=[file.stem],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "source": file.name,
                "type": "text",
            }
        ],
    )

    print(f"✓ {file.name}")


print("\nEmbedding selesai.")
```

Install dependensi:

```bash
pip install llama-cpp-python chromadb
```

---

## Alur kerja script

```text
chunk_0001.txt
│
├── Dibaca Python
│
├── "Llama.cpp adalah framework inferensi..."
│
├── llm.embed(text)
│
├── Hasil:
│   [0.12, -0.45, 0.88, ...]
│
├── Metadata:
│   source = chunk_0001.txt
│
└── collection.add(...)
    │
    └── ChromaDB
```

---

## Alur lengkap indexing

```text
Folder chunks/
│
├── chunk_0001.txt
├── chunk_0002.txt
└── chunk_0003.txt
     │
     ▼
Python Loop
     │
     ▼
llama.cpp (embedding model .gguf)
     │
     ▼
Vector
     │
     ▼
Metadata
     │
     ▼
Collection "knowledge"
     │
     ▼
chroma_db/
```

---

## Versi yang lebih efisien (batch embedding)

Jika jumlah chunk sangat banyak, lebih baik memproses sekaligus:

```python
from pathlib import Path

import chromadb
from llama_cpp import Llama


llm = Llama(
    model_path="models/bge-m3-q8_0.gguf",
    embedding=True,
    verbose=False,
)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("knowledge")


files = sorted(Path("chunks").glob("*.txt"))

ids = []
documents = []
metadatas = []

for file in files:
    text = file.read_text(encoding="utf-8").strip()

    if not text:
        continue

    ids.append(file.stem)
    documents.append(text)
    metadatas.append({
        "source": file.name
    })


# Embedding seluruh dokumen sekaligus
embeddings = llm.embed(documents)


collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
)

print(f"{len(ids)} chunk berhasil diindeks.")
```

Alurnya menjadi:

```text
chunks/
    │
    ├── chunk_0001
    ├── chunk_0002
    └── chunk_0003
            │
            ▼
    Kumpulkan semua teks
            │
            ▼
    llm.embed([...])
            │
            ▼
    Banyak vector sekaligus
            │
            ▼
    collection.add(...)
            │
            ▼
    ChromaDB
```

Model `.gguf` yang dipakai harus memang mendukung **embedding**, misalnya model BGE, Nomic Embed, atau model embedding lain yang dikonversi ke format GGUF. Model chat biasa seperti llama.cpp `Llama-3-Instruct` umumnya tidak ideal untuk tugas embedding.
