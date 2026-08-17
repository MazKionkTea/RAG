**Context Builder** adalah proses mengubah hasil pencarian dari ChromaDB menjadi teks konteks yang siap dimasukkan ke prompt LLM.

Alurnya:

```text
User Question
│
├── Embedding Question
│
├── ChromaDB Search
│
└── Top-K Chunk
    ├── chunk_001
    ├── chunk_015
    └── chunk_023
            │
            ▼
      Context Builder
            │
            ▼
      Context Siap Pakai
            │
            ▼
      Prompt Builder
            │
            ▼
         llama.cpp
```

---

# 1. Hasil dari ChromaDB

Misalnya:

```python
results = {
    "documents": [[
        "Untuk menginstal aplikasi gunakan sudo pacman -S nama-aplikasi.",

        "Pastikan koneksi internet aktif sebelum instalasi.",

        "Jika paket tidak ditemukan, lakukan pacman -Sy."
    ]],

    "metadatas": [[
        {"source": "manual.pdf", "page": 12},
        {"source": "faq.md", "section": "instalasi"},
        {"source": "tips.txt"}
    ]]
}
```

---

# 2. Tugas Context Builder

Tujuannya adalah:

```text
Chunk terpisah
↓
Gabungkan
↓
Beri nomor/sumber
↓
Batasi panjang context
↓
Hasilkan satu string besar
```

---

# 3. Context Builder Paling Sederhana

```python
context = "\n\n".join(
    results["documents"][0]
)
```

Hasil:

```text
Untuk menginstal aplikasi gunakan sudo pacman -S nama-aplikasi.

Pastikan koneksi internet aktif sebelum instalasi.

Jika paket tidak ditemukan, lakukan pacman -Sy.
```

---

# 4. Context Builder Dengan Nomor Referensi

Lebih umum digunakan:

```python
context_parts = []

for i, doc in enumerate(results["documents"][0], 1):
    context_parts.append(
        f"[{i}]\n{doc}"
    )

context = "\n\n".join(context_parts)
```

Hasil:

```text
[1]
Untuk menginstal aplikasi gunakan sudo pacman -S nama-aplikasi.

[2]
Pastikan koneksi internet aktif sebelum instalasi.

[3]
Jika paket tidak ditemukan, lakukan pacman -Sy.
```

---

# 5. Context Builder Dengan Metadata

Lebih informatif:

```python
context_parts = []

docs = results["documents"][0]
metas = results["metadatas"][0]

for i, (doc, meta) in enumerate(zip(docs, metas), 1):

    source = meta.get("source", "unknown")

    context_parts.append(
        f"[{i}] Source: {source}\n{doc}"
    )

context = "\n\n".join(context_parts)
```

Hasil:

```text
[1] Source: manual.pdf
Untuk menginstal aplikasi gunakan sudo pacman -S nama-aplikasi.

[2] Source: faq.md
Pastikan koneksi internet aktif sebelum instalasi.

[3] Source: tips.txt
Jika paket tidak ditemukan, lakukan pacman -Sy.
```

---

# 6. Membatasi Ukuran Context

LLM memiliki batas token.

Misalnya:

```text
Model:
8K context window
```

Tidak mungkin memasukkan 50 chunk sekaligus.

Karena itu biasanya:

```text
Top-20 hasil retrieval
↓
Ambil sampai 4000 token
↓
Sisanya dibuang
↓
Context Builder selesai
```

Contoh sederhana:

```python
MAX_CHARS = 5000

context = ""
current = 0

for doc in results["documents"][0]:

    if current + len(doc) > MAX_CHARS:
        break

    context += doc + "\n\n"
    current += len(doc)
```

---

# 7. Context Compression (Opsional)

RAG modern sering melakukan:

```text
20 chunk
↓
Ringkas tiap chunk
↓
Gabungkan
↓
Prompt LLM
```

Misalnya:

```text
Sebelum:

Chunk 1 = 1000 kata
Chunk 2 = 900 kata
Chunk 3 = 1200 kata

↓

Sesudah:

Chunk 1 = 200 kata
Chunk 2 = 150 kata
Chunk 3 = 180 kata
```

Tujuannya menghemat token.

---

# 8. Hasil Akhir Context Builder

Misalnya:

```text
[1] Source: manual.pdf

Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi


[2] Source: faq.md

Pastikan koneksi internet aktif sebelum instalasi.


[3] Source: tips.txt

Jika paket tidak ditemukan, lakukan:

pacman -Sy
```

Inilah yang disebut **context**.

---

# 9. Prompt Builder Menggunakan Context Tersebut

```python
prompt = f"""
Anda adalah asisten Linux.

Jawablah hanya berdasarkan konteks berikut.

KONTEKS:
{context}

PERTANYAAN:
Bagaimana cara menginstal aplikasi?
"""
```

Hasil:

```text
SYSTEM:
Anda adalah asisten Linux.

Jawablah hanya berdasarkan konteks berikut.

KONTEKS:

[1] Source: manual.pdf
Untuk menginstal aplikasi gunakan:
sudo pacman -S nama-aplikasi

[2] Source: faq.md
Pastikan koneksi internet aktif.

USER:
Bagaimana cara menginstal aplikasi?
```

---

# Ringkasan Sederhana

```text
ChromaDB
│
├── chunk_001
├── chunk_015
└── chunk_023
        │
        ▼
Context Builder
│
├── Gabungkan chunk
├── Tambahkan metadata
├── Beri nomor referensi
├── Batasi panjang token
└── Hasilkan satu string context
        │
        ▼
Prompt Builder
        │
        ▼
llama.cpp
```

Jadi, **Context Builder pada dasarnya adalah proses mengubah banyak chunk hasil retrieval menjadi satu blok teks terstruktur yang dapat dipahami dan digunakan oleh LLM untuk menghasilkan jawaban.**
