Tidak, **alur besarnya tetap sama**. Yang berbeda hanyalah **model embedding yang digunakan**.

---

# Jika menggunakan sentence-transformers

## Saat indexing

```text
Chunk
 └── sentence-transformers
      └── Vector
           └── ChromaDB
                └── Persistent Storage
```

Contoh:

```text
chunk_001.txt
↓
"ChromaDB adalah vector database"
↓
all-MiniLM-L6-v2
↓
[0.12, -0.45, 0.88, ...]
↓
ChromaDB
```

---

## Saat query

```text
Pertanyaan User
└── sentence-transformers
    └── Query Vector
        └── ChromaDB
            └── Top-K Chunk
                └── llama.cpp
                    └── Jawaban AI
```

---

# Aturan paling penting

Model embedding saat **indexing** dan **query** harus sama.

Benar:

```text
Indexing:
all-MiniLM-L6-v2
↓
ChromaDB

Query:
all-MiniLM-L6-v2
↓
ChromaDB
```

Salah:

```text
Indexing:
all-MiniLM-L6-v2
↓
ChromaDB

Query:
bge-m3.gguf
↓
ChromaDB
```

Karena vector dari dua model berbeda berada pada ruang semantik yang berbeda, hasil pencarian bisa menjadi buruk atau tidak relevan.

---

# Perbandingan alur

### 1. Menggunakan sentence-transformers

```text
INDEXING

Chunk
 └── sentence-transformers
      └── Vector
           └── ChromaDB


QUERY

Pertanyaan
 └── sentence-transformers
      └── Query Vector
           └── ChromaDB
                └── Top-K Chunk
                     └── llama.cpp
                          └── Jawaban
```

---

### 2. Menggunakan llama.cpp sepenuhnya

```text
INDEXING

Chunk
 └── bge-m3.gguf
      └── llama.cpp
           └── Vector
                └── ChromaDB


QUERY

Pertanyaan
 └── bge-m3.gguf
      └── llama.cpp
           └── Query Vector
                └── ChromaDB
                     └── Top-K Chunk
                          └── llama.cpp (chat model)
                               └── Jawaban
```

---

# Script query jika menggunakan sentence-transformers

```python
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer


# Inisialisasi model embedding
model = SentenceTransformer(
    "BAAI/bge-m3"
)

# Hubungkan ke ChromaDB
client = PersistentClient(path="chroma_db")

collection = client.get_collection(
    "knowledge"
)

# Pertanyaan user
question = input("Pertanyaan: ")

# Buat embedding pertanyaan
query_embedding = model.encode(
    question
).tolist()

# Cari Top-3
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

# Tampilkan hasil
for i, doc in enumerate(results["documents"][0], 1):
    print(f"\n[{i}]")
    print(doc)
```

---

# Perbedaan kode yang sebenarnya sangat kecil

Menggunakan sentence-transformers:

```python
model = SentenceTransformer("BAAI/bge-m3")

embedding = model.encode(text).tolist()
```

Menggunakan llama.cpp:

```python
model = Llama(
    model_path="bge-m3-q8_0.gguf",
    embedding=True
)

embedding = model.embed(text)
```

Selain dua baris itu, kode ChromaDB hampir identik:

```python
collection.add(...)
collection.query(...)
```

---

# Kesimpulan

```text
Chunk
    ↓
Embedding Model
    ↓
Vector
    ↓
ChromaDB
    ↓
Top-K Retrieval
    ↓
Prompt Builder
    ↓
llama.cpp
    ↓
Jawaban
```

Alur RAG **tidak berubah sama sekali**.

Yang berubah hanya:

```text
Embedding Model
```

bisa berupa:

* `sentence-transformers`
* `llama.cpp + model embedding GGUF`
* `OpenAI Embeddings`
* `Cohere Embeddings`
* `Jina Embeddings`
* `E5`
* `BGE`

Selama **model yang dipakai saat indexing dan query sama**, ChromaDB akan bekerja dengan benar.
