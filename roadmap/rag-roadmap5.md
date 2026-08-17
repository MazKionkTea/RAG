# Prompt Builder

**Prompt Builder** adalah proses menggabungkan:

* instruksi sistem,
* context dari ChromaDB,
* pertanyaan user,

menjadi **satu prompt final** yang dikirim ke llama.cpp.

---

## Alur Lengkap

```text id="n4k8zp"
User Question
│
├── Embedding Question
│
├── ChromaDB Search
│
├── Top-K Chunk
│
├── Context Builder
│   └── context
│
└── Prompt Builder
    └── final_prompt
            │
            ▼
        llama.cpp
            │
            ▼
        Jawaban AI
```

---

# 1. Input dari Context Builder

Misalnya:

```text id="b6s3vq"
context =

[1] Source: manual.pdf

Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi


[2] Source: faq.md

Pastikan koneksi internet aktif.


[3] Source: tips.txt

Jika paket tidak ditemukan,
jalankan pacman -Sy.
```

Dan pertanyaan user:

```text id="g8m2xt"
Bagaimana cara menginstal aplikasi?
```

---

# 2. Tugas Prompt Builder

```text id="w7q5na"
System Prompt
      +
Context
      +
User Question
      =
Final Prompt
```

---

# 3. Prompt Builder Paling Sederhana

```python
prompt = f"""
KONTEKS:

{context}

PERTANYAAN:

{question}
"""
```

Hasil:

```text id="m1z4cf"
KONTEKS:

[1]
Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi

[2]
Pastikan koneksi internet aktif.

PERTANYAAN:

Bagaimana cara menginstal aplikasi?
```

Ini bekerja, tetapi kurang optimal.

---

# 4. Menambahkan System Prompt

Biasanya RAG menggunakan instruksi khusus:

```python
SYSTEM_PROMPT = """
Anda adalah asisten Linux.

Jawablah HANYA berdasarkan konteks.

Jika informasi tidak ditemukan,
katakan:

"Saya tidak menemukan informasi tersebut
dalam dokumen."

Jangan mengarang jawaban.
"""
```

---

Kemudian Prompt Builder:

```python
prompt = f"""
{SYSTEM_PROMPT}

KONTEKS:

{context}

PERTANYAAN:

{question}
"""
```

---

Hasil:

```text id="k3r7pm"
Anda adalah asisten Linux.

Jawablah HANYA berdasarkan konteks.

Jika informasi tidak ditemukan,
katakan:

"Saya tidak menemukan informasi tersebut
dalam dokumen."

Jangan mengarang jawaban.


KONTEKS:

[1]
Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi


[2]
Pastikan koneksi internet aktif.


PERTANYAAN:

Bagaimana cara menginstal aplikasi?
```

---

# 5. Prompt Builder dengan Citation

Agar LLM menyebut sumber:

```python
SYSTEM_PROMPT = """
Gunakan nomor referensi [1], [2], [3]
saat menjawab.

Contoh:

Menurut [1], instalasi dilakukan
dengan menjalankan:

sudo pacman -S paket
"""
```

---

Context:

```text id="f8p6vw"
[1] manual.pdf
sudo pacman -S nama-aplikasi

[2] faq.md
Pastikan internet aktif.
```

---

Kemungkinan output:

```text id="y5n8sx"
Menurut [1], aplikasi dapat diinstal
menggunakan:

sudo pacman -S nama-aplikasi

Selain itu, [2] menyarankan agar
koneksi internet aktif sebelum instalasi.
```

---

# 6. Prompt Builder Berbasis Template

Biasanya dibuat sebagai fungsi:

```python
def build_prompt(context, question):

    return f"""
Anda adalah asisten Linux.

Aturan:
- Gunakan hanya informasi dari konteks.
- Jangan mengarang.
- Jika tidak tahu, katakan tidak tahu.

KONTEKS:
{context}

PERTANYAAN:
{question}

JAWABAN:
"""
```

Penggunaan:

```python
prompt = build_prompt(
    context,
    question
)
```

---

# 7. Alur Internal Prompt Builder

```text id="u9n4ge"
System Prompt
│
├── "Jangan mengarang"
│
├── "Gunakan konteks"
│
└── "Sebutkan sumber"
        │
        ▼

Context
│
├── [1] manual.pdf
├── [2] faq.md
└── [3] tips.txt
        │
        ▼

User Question
│
└── "Bagaimana cara menginstal aplikasi?"
        │
        ▼

Final Prompt
```

---

# 8. Final Prompt yang Dikirim ke llama.cpp

```text id="e7m2xa"
SYSTEM:

Anda adalah asisten Linux.

Aturan:
- Gunakan hanya informasi dari konteks.
- Jangan mengarang.
- Jika informasi tidak tersedia,
  katakan tidak ditemukan.


CONTEXT:

[1] manual.pdf

Untuk menginstal aplikasi gunakan:

sudo pacman -S nama-aplikasi


[2] faq.md

Pastikan koneksi internet aktif.


USER:

Bagaimana cara menginstal aplikasi?


ASSISTANT:
```

Inilah yang benar-benar diterima oleh model.

---

# 9. Dikirim ke llama.cpp

Contoh sederhana:

```python
from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-3.gguf",
    n_ctx=8192
)

response = llm(
    prompt,
    max_tokens=512
)

print(
    response["choices"][0]["text"]
)
```

---

# 10. Jawaban Akhir

```text id="r4t6kn"
Menurut [1], aplikasi dapat diinstal
dengan menjalankan:

sudo pacman -S nama-aplikasi

Selain itu, [2] menyarankan agar
koneksi internet aktif sebelum memulai
proses instalasi.
```

---

# Ringkasan

```text id="x2v8bc"
Top-K Chunk
│
├── [1] manual.pdf
├── [2] faq.md
└── [3] tips.txt
        │
        ▼
Context Builder
        │
        ▼
System Prompt
        +
Context
        +
User Question
        │
        ▼
Prompt Builder
        │
        ▼
Final Prompt
        │
        ▼
llama.cpp
        │
        ▼
Jawaban AI
```

Jadi, **Prompt Builder adalah jembatan antara hasil retrieval dan proses generasi oleh LLM**. Tanpa Prompt Builder, LLM hanya menerima potongan teks mentah dan tidak tahu aturan apa yang harus diikuti saat menjawab.
