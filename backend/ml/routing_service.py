import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.ml.embedding_service import get_text_embedding


from sqlalchemy.orm import Session
from backend.models import Officer
from backend.db import SessionLocal


def route_to_best_officer(complaint_text: str):

    db: Session = SessionLocal()
    officers = db.query(Officer).all()

    complaint_embedding = get_text_embedding(complaint_text)

    best_score = -1
    best_officer = None

    for officer in officers:

        officer_profile_text = officer.skills

        officer_embedding = get_text_embedding(officer_profile_text)

        similarity = cosine_similarity(
            [complaint_embedding],
            [officer_embedding]
        )[0][0]

        workload_penalty = 1 / (1 + officer.current_workload)

        final_score = similarity * workload_penalty

        if final_score > best_score:
            best_score = final_score
            best_officer = officer

    db.close()
    return best_officer
