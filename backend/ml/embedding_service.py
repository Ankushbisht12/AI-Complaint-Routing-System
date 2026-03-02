from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once (global)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_text_embedding(text: str) -> np.ndarray:
    """
    Convert text into embedding vector
    """
    embedding = model.encode(text)
    return embedding


def get_batch_embeddings(texts: list) -> np.ndarray:
    """
    Convert multiple texts into embeddings
    """
    embeddings = model.encode(texts)
    return embeddings