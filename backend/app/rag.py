"""
RAG (Retrieval Augmented Generation) implementation.
AI helped with: the cosine similarity calculation and chunking strategy.
I handled the embedding storage and search logic based on understanding of vector search.
"""
import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings", "index.json")

chunks = []
embeddings_matrix = None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words = text.split()
    result = []

    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        if len(chunk.strip()) > 50:
            result.append(chunk)
        i += chunk_size - overlap

    return result


def get_embedding(text: str) -> list:
    text = text.replace("\n", " ").strip()
    if not text:
        return [0] * 1536

    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def init_rag():
    global chunks, embeddings_matrix

    os.makedirs(os.path.join(DATA_DIR, "embeddings"), exist_ok=True)

    if os.path.exists(EMBEDDINGS_FILE):
        print("Loading existing embeddings...")
        with open(EMBEDDINGS_FILE, "r") as f:
            data = json.load(f)
            chunks = data["chunks"]
            embeddings_matrix = np.array(data["embeddings"])
        print(f"Loaded {len(chunks)} chunks")
        return

    source_file = os.path.join(DATA_DIR, "cape_town_data.txt")
    if not os.path.exists(source_file):
        print("No source data found, RAG will be empty")
        return

    print("Building embeddings from source data...")
    with open(source_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = chunk_text(raw_text)
    print(f"Created {len(chunks)} chunks")

    embeddings = []
    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            print(f"Processing chunk {i}/{len(chunks)}")
        emb = get_embedding(chunk)
        embeddings.append(emb)

    embeddings_matrix = np.array(embeddings)

    with open(EMBEDDINGS_FILE, "w") as f:
        json.dump({
            "chunks": chunks,
            "embeddings": embeddings_matrix.tolist()
        }, f)

    print("Embeddings saved")


def search_documents(query: str, top_k: int = 3) -> list:
    global chunks, embeddings_matrix

    if embeddings_matrix is None or len(chunks) == 0:
        return []

    query_embedding = np.array(get_embedding(query))

    query_norm = query_embedding / np.linalg.norm(query_embedding)
    embeddings_norm = embeddings_matrix / np.linalg.norm(embeddings_matrix, axis=1, keepdims=True)

    similarities = np.dot(embeddings_norm, query_norm)

    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "text": chunks[idx],
            "score": float(similarities[idx]),
            "index": int(idx)
        })

    return results
