from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base
import enum


# Role Enum
class UserRole(str, enum.Enum):
    user = "user"
    officer = "officer"
    admin = "admin"


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    flat_number = Column(String(10))
    role = Column(Enum(UserRole))
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="user")



# Officer Table
class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    department = Column(String(100))
    skills = Column(String(255))
    avg_resolution_days = Column(Float)
    current_workload = Column(Integer, default=0)

    complaints = relationship("Complaint", back_populates="officer")



# Complaint Status Enum
class ComplaintStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"

# Complaint Table
class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # Core
    text = Column(String(1000))
    language = Column(String(50), default="English")
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ML Predictions
    predicted_priority = Column(String(20))
    predicted_eta_days = Column(Float)
    officer_id = Column(Integer, ForeignKey("officers.id"))

    # Ground Truth (for evaluation)
    actual_priority = Column(String(20), nullable=True)
    actual_resolution_days = Column(Float, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Status Tracking
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.pending)

    # Relations
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="complaints")
    officer = relationship("Officer")