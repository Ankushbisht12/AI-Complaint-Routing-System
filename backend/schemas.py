from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Complaint Schema
class ComplaintBase(BaseModel):
    user_id: str
    text: str
    language: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None



class ComplaintCreate(BaseModel):
    text: Optional[str] = None
    language: Optional[str] = None
    location: str

class ComplaintDB(ComplaintBase):
    complaint_id: str
    timestamp: datetime
    assigned_officer_id: Optional[str] = None
    priority: Optional[str] = None
    predicted_eta_days: Optional[int] = None

    class Config:
        orm_mode = True


# Officer Schema
class OfficerBase(BaseModel):
    name: str
    department: str
    skills: List[str]
    languages: List[str]
    location: str
    experience_years: int
    avg_resolution_days: float
    current_workload: int


class OfficerCreate(OfficerBase):
    pass


class OfficerDB(OfficerBase):
    officer_id: str

    class Config:
        orm_mode = True


# Prediction Output Schema
class RoutingResponse(BaseModel):
    complaint_id: str
    assigned_officer: str
    priority: str
    predicted_eta_days: int
    similar_complaints: List[str]

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    flat_number: str


class UserLogin(BaseModel):
    email: str
    password: str    