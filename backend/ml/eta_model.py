import joblib
from sentence_transformers import SentenceTransformer

print("Loading ETA Model...")
regressor = joblib.load("eta_model.pkl")

print("Loading Embedding Model for ETA...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def predict_eta(text: str):

    embedding = embedding_model.encode([text])
    prediction = regressor.predict(embedding)

    return int(round(prediction[0]))