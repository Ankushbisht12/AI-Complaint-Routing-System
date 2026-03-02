import uuid
from datetime import datetime
from typing import List
from backend.schemas import OfficerDB, ComplaintDB

# In-memory storage
OFFICERS: List[OfficerDB] = []
COMPLAINTS: List[ComplaintDB] = []

# Create Dummy Officers
def load_dummy_officers():
    global OFFICERS

    OFFICERS = [
        OfficerDB(
            officer_id=str(uuid.uuid4()),
            name="Rajesh Kumar",
            department="Road Safety",
            skills=["traffic", "accident", "road damage"],
            languages=["hindi", "english"],
            location="Delhi",
            experience_years=8,
            avg_resolution_days=3.5,
            current_workload=5
        ),
        OfficerDB(
            officer_id=str(uuid.uuid4()),
            name="Anita Sharma",
            department="Water Supply",
            skills=["water leakage", "pipeline", "drainage"],
            languages=["hindi", "english"],
            location="Delhi",
            experience_years=5,
            avg_resolution_days=4.0,
            current_workload=3
        ),
        OfficerDB(
            officer_id=str(uuid.uuid4()),
            name="Mohammed Khan",
            department="Electricity",
            skills=["power outage", "electric pole", "transformer"],
            languages=["hindi", "english", "urdu"],
            location="Delhi",
            experience_years=10,
            avg_resolution_days=2.5,
            current_workload=7
        ),
    ]


# Add Complaint
def add_complaint(complaint: ComplaintDB):
    COMPLAINTS.append(complaint)


def get_officers():
    return OFFICERS


def get_complaints():
    return COMPLAINTS