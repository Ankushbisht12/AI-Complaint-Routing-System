import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error

from sentence_transformers import SentenceTransformer


print("Loading dataset...")
df = pd.read_csv("training_data.csv")

print("Loading embedding model...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Generating embeddings...")
X_embeddings = embedding_model.encode(df["text"].tolist())


# PRIORITY CLASSIFICATION
print("\nTraining Priority Classifier...")

y_priority = df["priority"]

X_train, X_test, y_train, y_test = train_test_split(
    X_embeddings, y_priority, test_size=0.2, random_state=42
)

classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")

print("Priority Model Accuracy:", accuracy)
print("Priority Model F1 Score:", f1)

joblib.dump(classifier, "priority_model.pkl")



# ETA REGRESSION
print("\nTraining ETA Regressor...")

y_eta = df["eta_days"]

X_train_eta, X_test_eta, y_train_eta, y_test_eta = train_test_split(
    X_embeddings, y_eta, test_size=0.2, random_state=42
)

regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(X_train_eta, y_train_eta)

y_eta_pred = regressor.predict(X_test_eta)

mae = mean_absolute_error(y_test_eta, y_eta_pred)

print("ETA Model MAE:", mae)

joblib.dump(regressor, "eta_model.pkl")

print("\nModels saved successfully!")