import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    confusion_matrix,
    classification_report
)
from sqlalchemy.orm import Session
from backend.models import Complaint

def evaluate_models(db: Session):

    complaints = db.query(Complaint).filter(
        Complaint.actual_priority.isnot(None),
        Complaint.actual_resolution_days.isnot(None)
    ).all()

    if len(complaints) == 0:
        return {"message": "No resolved complaints available for evaluation"}

    y_true_priority = []
    y_pred_priority = []

    y_true_eta = []
    y_pred_eta = []

    for c in complaints:
        y_true_priority.append(c.actual_priority)
        y_pred_priority.append(c.predicted_priority)

        y_true_eta.append(c.actual_resolution_days)
        y_pred_eta.append(c.predicted_eta_days)

    # Classification Metrics
    accuracy = accuracy_score(y_true_priority, y_pred_priority)
    f1 = f1_score(y_true_priority, y_pred_priority, average="weighted")

    labels = list(set(y_true_priority + y_pred_priority))
    cm = confusion_matrix(y_true_priority, y_pred_priority, labels=labels)

    # Regression Metric
    mae = mean_absolute_error(y_true_eta, y_pred_eta)

    report = classification_report(
    y_true_priority,
    y_pred_priority,
    output_dict=True 
    )

    return {
        "classification_report": report,
        "total_evaluated": len(complaints),
        "priority_metrics": {
            "accuracy": round(float(accuracy), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": {
                "labels": labels,
                "matrix": cm.tolist()
            }
        },
        "eta_metrics": {
            "mae": round(float(mae), 4)
        }
        
    }