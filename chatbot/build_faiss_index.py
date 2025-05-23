from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def split_text(text, max_chars=1000):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += "\n\n" + para
        else:
            chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    return chunks

def main():
    file_path = os.path.join(os.path.dirname(__file__), "orange[1].txt")
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = split_text(text)
    embeddings = model.encode(chunks, show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype="float32"))
    faiss.write_index(index, "orange_index.faiss")
    with open("orange_chunks.txt", "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(chunks))

if __name__ == "__main__":
    main()
