import faiss
import numpy as np
from backend.ml.embedding_service import get_text_embedding
from backend.database import get_complaints

# FAISS index (384 = embedding size)
dimension = 384
index = faiss.IndexFlatL2(dimension)

# Store complaint IDs in same order
complaint_id_store = []


def add_complaint_to_index(complaint_id: str, text: str):
    embedding = get_text_embedding(text).astype("float32")
    index.add(np.array([embedding]))
    complaint_id_store.append(complaint_id)

def find_similar_complaints(text: str, top_k: int = 3):
    if index.ntotal == 0:
        return []

    embedding = get_text_embedding(text).astype("float32")
    distances, indices = index.search(np.array([embedding]), top_k + 5)

    unique_ids = []
    seen = set()

    for idx in indices[0]:
        if idx < len(complaint_id_store):
            cid = complaint_id_store[idx]

            # Remove duplicates
            if cid not in seen:
                seen.add(cid)
                unique_ids.append(cid)

        if len(unique_ids) == top_k:
            break

    return unique_ids