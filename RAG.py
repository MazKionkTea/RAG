import os, requests, chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="rag_chunks")
folder = "./path_folder_md" 

for idx, file in enumerate(os.listdir(folder)):
    if file.endswith(".md"):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            text = f.read()

        # Request embedding ke llama-server
        res = requests.post("http://localhost:8080/embedding", json={"content": text}).json()

        # Simpan teks dan vektor ke ChromaDB
        collection.add(
            embeddings=[res["embedding"]],
            documents=[text],
            ids=[f"id_{idx}"]
        )
