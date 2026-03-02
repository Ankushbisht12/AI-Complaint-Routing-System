import re
from langdetect import detect
from backend.ml.embedding_service import get_text_embedding

def clean_text(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def detect_language(text: str):
    try:
        return detect(text)
    except:
        return "unknown"

def extract_structured_features(text: str):
    keywords = ["blast", "fire", "leakage", "accident", "outage"]
    keyword_flags = {k: int(k in text.lower()) for k in keywords}
    text_length = len(text)
    return {
        "length": text_length,
        **keyword_flags
    }

def build_features(text: str):
    cleaned = clean_text(text)
    language = detect_language(cleaned)
    structured = extract_structured_features(cleaned)
    embedding = get_text_embedding(cleaned)

    return {
        "clean_text": cleaned,
        "language": language,
        "structured_features": structured,
        "embedding": embedding
    }

def process_audio(audio_path: str):
    # Placeholder for future speech-to-text
    return {"audio_transcript": "not_implemented"}

def process_video(video_path: str):
    # Placeholder for future vision extraction
    return {"video_summary": "not_implemented"}