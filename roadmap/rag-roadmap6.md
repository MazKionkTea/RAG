# llama.cpp (Generation)

Setelah **Prompt Builder** selesai, tahap berikutnya adalah **Generation**, yaitu proses LLM menghasilkan jawaban berdasarkan prompt yang sudah dibuat.

---

# Alur Lengkap Sampai Generation

```text id="8k2x4p"
Dokumen
│
├── Chunking
├── Embedding
└── ChromaDB


User Question
│
├── Embedding Question
├── Similarity Search
├── Top-K Chunk
├── Context Builder
├── Prompt Builder
└── llama.cpp (Generation)
        │
        ▼
   Final Answer
```

---

# 1. Input dari Prompt Builder

Misalnya Prompt Builder menghasilkan:

```text id="7f3m8q"
SYSTEM:

Anda adalah asisten Linux.

Aturan:
- Gunakan hanya informasi dari konteks.
- Jangan mengarang jawaban.
- Jika informasi tidak ditemukan,
  katakan bahwa informasi tidak tersedia.


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

Ini adalah **prompt final** yang akan diberikan ke model.

---

# 2. Tugas llama.cpp

```text id="c4r9ny"
Final Prompt
        │
        ▼
Tokenization
        │
        ▼
Inference
        │
        ▼
Token Generation
        │
        ▼
Jawaban Lengkap
```

---

# 3. Tokenization

Sebelum diproses, teks diubah menjadi token.

```text id="v8p1dw"
"Bagaimana cara menginstal aplikasi?"

↓

[912, 4412, 1287, 551, 9921, 13]
```

LLM bekerja dengan token, bukan karakter atau kata.

---

# 4. Inference

Model menghitung probabilitas token berikutnya.

```text id="p3s7ha"
ASSISTANT:
Untuk
```

Model memilih token pertama.

Lalu:

```text id="w1n8kb"
ASSISTANT:
Untuk menginstal
```

Kemudian:

```text id="q9d4mc"
ASSISTANT:
Untuk menginstal aplikasi
```

Proses ini berlangsung satu token demi satu token.

---

# 5. Generation Loop

Secara konseptual:

```text id="m6t2vz"
Prompt
│
├── Token #1
├── Token #2
├── Token #3
├── Token #4
└── ...
```

Sampai salah satu kondisi tercapai:

```text id="t8k5rw"
Berhenti jika:

├── max_tokens tercapai
├── EOS token ditemukan
├── stop sequence ditemukan
└── User menghentikan proses
```

---

# 6. Script Python Sederhana

Menggunakan `llama-cpp-python`:

```python
from llama_cpp import Llama


llm = Llama(
    model_path="models/llama-3.gguf",
    n_ctx=8192,
    n_gpu_layers=-1,
    verbose=False,
)


response = llm(
    prompt,
    max_tokens=512,
    temperature=0.3,
)


answer = response["choices"][0]["text"]

print(answer)
```

---

# 7. Streaming Generation

Lebih umum pada chatbot.

```python
for chunk in llm(
    prompt,
    stream=True,
    max_tokens=512,
):

    token = chunk["choices"][0]["text"]

    print(token, end="", flush=True)
```

---

Alurnya:

```text id="f2v7cs"
Prompt
│
▼

llama.cpp
│
├── Token: "Untuk"
├── Token: " menginstal"
├── Token: " aplikasi"
├── Token: " gunakan"
└── ...
```

User melihat jawaban muncul secara real-time.

---

# 8. Parameter Generation

Beberapa parameter penting:

| Parameter        | Fungsi                   |
| ---------------- | ------------------------ |
| `max_tokens`     | Panjang jawaban maksimum |
| `temperature`    | Tingkat kreativitas      |
| `top_k`          | Jumlah kandidat token    |
| `top_p`          | Probabilitas kumulatif   |
| `repeat_penalty` | Mengurangi pengulangan   |
| `stop`           | Token penghenti          |

---

Contoh:

```python
response = llm(
    prompt,
    max_tokens=512,
    temperature=0.2,
    top_p=0.95,
    repeat_penalty=1.1,
    stop=["USER:"],
)
```

Untuk RAG biasanya:

```text id="x5n4jr"
temperature = 0.1 - 0.3
```

Karena kita ingin jawaban faktual, bukan kreatif.

---

# 9. Chat Template (Modern)

Model modern biasanya memakai format chat.

Contoh:

```python
messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": f"""
KONTEKS:

{context}

PERTANYAAN:

{question}
"""
    }
]


response = llm.create_chat_completion(
    messages=messages,
    temperature=0.2,
)
```

---

Alurnya:

```text id="n7c3ka"
System Message
        +
User Message
        │
        ▼
Chat Template
        │
        ▼
Prompt Internal
        │
        ▼
llama.cpp
        │
        ▼
Jawaban
```

---

# 10. Hasil Akhir

Output:

```text id="r5k8me"
Menurut [1], aplikasi dapat diinstal
dengan menjalankan:

sudo pacman -S nama-aplikasi

Selain itu, [2] menyarankan agar
koneksi internet aktif sebelum memulai
instalasi.
```

---

# Generation Bukan Retrieval

Penting untuk membedakan:

```text id="u2m4pw"
ChromaDB
=
Mencari informasi


llama.cpp
=
Menulis jawaban menggunakan informasi tersebut
```

atau:

```text id="d8v1hs"
ChromaDB
→ librarian (pustakawan)

llama.cpp
→ penulis yang merangkai jawaban
```

---

# Ringkasan Seluruh Pipeline RAG

```text id="g9q7tb"
INDEXING
────────────────────────

Dokumen
↓
Chunking
↓
Embedding
↓
ChromaDB


QUERY
────────────────────────

Pertanyaan User
↓
Embedding Pertanyaan
↓
Similarity Search
↓
Top-K Chunk
↓
Context Builder
↓
Prompt Builder
↓
llama.cpp (Generation)
↓
Final Answer
```

Sampai titik ini, Anda sudah memiliki **pipeline RAG minimal yang lengkap**: dari dokumen mentah hingga jawaban akhir yang dihasilkan oleh LLM.
