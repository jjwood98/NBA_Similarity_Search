import faiss
import numpy as np
import pickle
import pandas as pd
import os

def build_faiss_index(embeddings, save_path="faiss_index.index"):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)   # simple L2 distance
    index.add(embeddings)
    faiss.write_index(index, save_path)
    return index

def load_faiss_index(index_path="faiss_index.index"):
    metadata_path = index_path.replace(".bin", "_metadata.parquet")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index {index_path} not found.")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata {metadata_path} not found.")

    index = faiss.read_index(index_path)
    metadata = pd.read_parquet(metadata_path)

    return index, metadata

def query_faiss(index, query_embedding, k=5):
    query_embedding = np.atleast_2d(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, k)
    return distances, indices

def save_faiss_index(index, filepath="faiss_index.bin", metadata=None):
    faiss.write_index(index, filepath)

    # Save metadata (player names, etc.)
    if metadata is not None:
        with open(filepath.replace(".bin", "_meta.pkl"), "wb") as f:
            pickle.dump(metadata, f)

