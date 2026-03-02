from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

from backend.db import engine, get_db, SessionLocal
from backend.models import Base, User, Officer, Complaint, UserRole
from backend.schemas import ComplaintCreate, UserRegister
from backend.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from fastapi.security import OAuth2PasswordRequestForm

from backend.ml.priority_model import predict_priority
from backend.ml.eta_model import predict_eta
from backend.ml.routing_service import route_to_best_officer
from backend.ml.similarity_service import (
    add_complaint_to_index,
    find_similar_complaints
)

app = FastAPI(
    title="AI Complaint Routing System",
    version="1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: Create Tables
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    if db.query(Officer).count() == 0:
        officers = [
            Officer(
                name="Rajesh Kumar",
                department="Road Safety",
                skills="traffic,accident,road damage",
                avg_resolution_days=3.5,
                current_workload=5
            ),
            Officer(
                name="Anita Sharma",
                department="Water Supply",
                skills="water leakage,pipeline,drainage",
                avg_resolution_days=4.0,
                current_workload=3
            ),
            Officer(
                name="Mohammed Khan",
                department="Electricity",
                skills="power outage,electric pole,transformer",
                avg_resolution_days=2.5,
                current_workload=7
            )
        ]
        db.add_all(officers)
        db.commit()

    db.close()

# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return {"message": "Complaint Routing System Running"}

# -------------------------
# Register
# -------------------------
@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        flat_number=user.flat_number,
        role=UserRole.user
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}

# -------------------------
# Login
# -------------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        db.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user.password_hash):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
    data={
        "sub": user.email,
        "role": user.role.value
    }
)

    db.close()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



from fastapi import UploadFile, File
from backend.ml.audio_service import transcribe_audio, extract_audio_from_video
import shutil
import os

# Submit Complaint
@app.post("/submit-complaint")
def submit_complaint(
    location: str,
    text: str = None,
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # If audio/video uploaded
    if file:

        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith(".mp4"):
            audio_path = extract_audio_from_video(file_path)
            text = transcribe_audio(audio_path)
            os.remove(audio_path)
        else:
            text = transcribe_audio(file_path)

        os.remove(file_path)

    if not text:
        raise HTTPException(status_code=400, detail="No complaint content provided")

    # Continue normal ML pipeline
    similar_complaints = find_similar_complaints(text)
    best_officer = route_to_best_officer(text)
    priority = predict_priority(text)
    eta_days = predict_eta(text)

    new_complaint = Complaint(
        text=text,
        language="auto",
        location=location,
        predicted_priority=priority,
        predicted_eta_days=eta_days,
        officer_id=best_officer.id,
        status="pending",
        user_id=current_user.id
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    add_complaint_to_index(str(new_complaint.id), text)

    return {
        "complaint_id": new_complaint.id,
        "transcribed_text": text,
        "assigned_officer": best_officer.name,
        "priority": priority,
        "predicted_eta_days": eta_days,
        "similar_complaints": similar_complaints
    }


from backend.models import Complaint, ComplaintStatus
from fastapi import Path

@app.put("/resolve-complaint/{complaint_id}")
def resolve_complaint(
    complaint_id: int = Path(...),
    actual_priority: str = None,
    actual_resolution_days: float = None,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.actual_priority = actual_priority
    complaint.actual_resolution_days = actual_resolution_days
    complaint.resolved_at = datetime.utcnow()
    complaint.status = ComplaintStatus.resolved

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint marked as resolved"}    


from backend.ml.evaluation_service import evaluate_models

@app.get("/evaluate-model")
def evaluate_model(db: Session = Depends(get_db)):
    return evaluate_models(db)



@app.get("/complaints")
def get_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.admin:
        complaints = db.query(Complaint).all()
    else:
        complaints = db.query(Complaint).filter(
            Complaint.user_id == current_user.id
        ).all()

    return complaints