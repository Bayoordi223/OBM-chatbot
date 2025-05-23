from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def search_similar_chunks(query: str, top_k=3):
    index = faiss.read_index("orange_index.faiss")
    with open("orange_chunks.txt", "r", encoding="utf-8") as f:
        chunks = f.read().split("\n\n---\n\n")
    emb = model.encode([query])
    D, I = index.search(np.array(emb, dtype="float32"), top_k)
    return [chunks[i] for i in I[0]]
