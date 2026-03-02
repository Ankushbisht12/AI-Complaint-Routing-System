import joblib
from sentence_transformers import SentenceTransformer

print("Loading Priority Model...")
classifier = joblib.load("priority_model.pkl")

print("Loading Embedding Model for Priority...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def predict_priority(text: str):

    embedding = embedding_model.encode([text])
    prediction = classifier.predict(embedding)

    return prediction[0]