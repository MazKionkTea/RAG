# 1. Proses Memasukkan Data ke ChromaDB (Indexing)

```text
Chunk
 └── Embedding Model
      └── Vector
           └── Metadata
                └── Chroma Collection
                     └── Persistent Storage
```

Penjelasan sederhananya:

```text
Chunk
```

* Dokumen yang panjang sudah dipotong menjadi bagian-bagian kecil.
* Misalnya:

```text
Chunk_001:
"Llama.cpp adalah framework inferensi LLM."

Chunk_002:
"ChromaDB digunakan untuk menyimpan vector embedding."
```

---

```text
└── Embedding Model
```

* Setiap chunk dikirim ke model embedding.
* Tugas model embedding adalah mengubah teks menjadi representasi angka yang bisa dipahami komputer.

Contoh:

```text
"Llama.cpp adalah framework inferensi LLM."
↓
Embedding Model (BGE-M3)
↓
Vector
```

---

```text
      └── Vector
```

* Hasil embedding berupa daftar angka.

Contoh:

```text
[0.12, -0.53, 0.88, 0.01, ...]
```

* Vector ini menyimpan makna semantik teks, bukan sekadar kata-kata.

---

```text
           └── Metadata
```

* Informasi tambahan tentang chunk tersebut.

Contoh:

```text
source   = manual.pdf
page     = 12
chunk_id = 001
category = installation
```

* Metadata membantu pencarian dan pelacakan sumber jawaban.

---

```text
                └── Chroma Collection
```

* ChromaDB menyimpan data dalam bentuk collection (mirip tabel pada database biasa).

Contoh:

```text
Collection: knowledge_base

├── chunk_001
├── chunk_002
└── chunk_003
```

Setiap item berisi:

```text
ID
Text
Vector
Metadata
```

---

```text
                     └── Persistent Storage
```

* Data akhirnya disimpan ke disk.

Contoh:

```text
project/
└── chroma_db/
    ├── chroma.sqlite3
    └── index/
```

* Jadi, ketika program dimatikan, embedding tidak perlu dibuat ulang.

---

## Ringkasan Sederhana

```text
Dokumen
↓
Dipotong menjadi chunk
↓
Setiap chunk diubah menjadi vector
↓
Ditambah informasi sumber (metadata)
↓
Disimpan ke collection ChromaDB
↓
Disimpan permanen di harddisk
```

---

# 2. Proses Menjawab Pertanyaan User (Retrieval + Generation)

```text
Pertanyaan User
└── Embedding Pertanyaan
    └── Similarity Search (Top-K)
        └── ChromaDB
            └── Chunk Relevan
                └── Prompt Builder
                    └── llama.cpp
                        └── Jawaban AI
```

Penjelasan sederhananya:

---

```text
Pertanyaan User
```

User bertanya:

```text
"Bagaimana cara menginstal aplikasi?"
```

---

```text
└── Embedding Pertanyaan
```

Pertanyaan diubah menjadi vector menggunakan model embedding yang sama.

```text
"Bagaimana cara menginstal aplikasi?"
↓
Embedding Model
↓
[0.41, -0.82, 0.17, ...]
```

Tujuannya agar pertanyaan dan dokumen berada dalam "bahasa angka" yang sama.

---

```text
    └── Similarity Search (Top-K)
```

* Sistem mencari vector yang paling mirip.
* Top-K berarti mengambil K hasil terbaik.

Misalnya:

```text
Top-3:

1. chunk_015 (95%)
2. chunk_008 (92%)
3. chunk_027 (88%)
```

---

```text
        └── ChromaDB
```

ChromaDB melakukan pencarian:

```text
Vector pertanyaan
↓
Bandingkan dengan ribuan vector dokumen
↓
Ambil yang paling dekat
```

Bukan mencari kata yang sama, tetapi makna yang paling mirip.

Misalnya:

```text
Pertanyaan:
"Bagaimana memasang aplikasi?"

Dokumen:
"Cara instal program di Linux"

→ tetap dianggap mirip.
```

---

```text
            └── Chunk Relevan
```

Hasil pencarian:

```text
Chunk_015:
"Untuk menginstal aplikasi, jalankan:

sudo pacman -S nama-aplikasi"
```

Inilah konteks yang akan diberikan ke LLM.

---

```text
                └── Prompt Builder
```

Sistem menggabungkan konteks dengan pertanyaan user.

Contoh:

```text
SYSTEM:
Jawablah berdasarkan informasi berikut.

CONTEXT:
Untuk menginstal aplikasi, jalankan:

sudo pacman -S nama-aplikasi

USER:
Bagaimana cara menginstal aplikasi?
```

---

```text
                    └── llama.cpp
```

Prompt tersebut dikirim ke model GGUF melalui llama.cpp.

```text
Prompt lengkap
↓
llama.cpp
↓
Inference
```

Model tidak mencari data lagi; ia hanya menggunakan konteks yang sudah diberikan.

---

```text
                        └── Jawaban AI
```

Hasil akhirnya:

```text
Untuk menginstal aplikasi, jalankan:

sudo pacman -S nama-aplikasi

Pastikan koneksi internet aktif sebelum proses instalasi.
```

---

# Ringkasan Sederhana

```text
User bertanya
↓
Pertanyaan diubah menjadi vector
↓
ChromaDB mencari chunk yang paling mirip
↓
Chunk relevan diambil
↓
Chunk + pertanyaan digabung menjadi prompt
↓
Prompt dikirim ke llama.cpp
↓
LLM menghasilkan jawaban
```

Atau dalam satu alur lengkap:

```text
INDEXING (sekali saja)

Dokumen
↓
Chunk
↓
Embedding
↓
Metadata
↓
ChromaDB
↓
Disimpan ke disk


QUERY (setiap user bertanya)

Pertanyaan
↓
Embedding pertanyaan
↓
Cari vector terdekat di ChromaDB
↓
Ambil chunk relevan
↓
Gabungkan menjadi prompt
↓
llama.cpp
↓
Jawaban AI
```
