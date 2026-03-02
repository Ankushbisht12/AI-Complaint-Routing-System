import random
import pandas as pd

categories = {
    "Electricity": [
        "Transformer blast in area",
        "Power outage since morning",
        "Electric pole sparking",
        "Frequent voltage fluctuation",
        "Meter not working"
    ],
    "Water Supply": [
        "Water leakage in pipeline",
        "No water supply since 2 days",
        "Drain overflow issue",
        "Low water pressure",
        "Broken water valve"
    ],
    "Road Maintenance": [
        "Huge pothole causing accidents",
        "Road damaged after rain",
        "Street light not working",
        "Broken speed breaker",
        "Cracked pavement"
    ],
    "Sanitation": [
        "Garbage not collected",
        "Sewage overflow",
        "Dustbin broken",
        "Unclean public toilet",
        "Dead animal on road"
    ]
}

high_keywords = ["blast", "accident", "fire", "injured", "emergency"]
medium_keywords = ["outage", "leakage", "overflow", "damaged"]
low_keywords = ["minor", "slow", "small"]

def assign_priority(text):
    text_lower = text.lower()

    if any(word in text_lower for word in high_keywords):
        return "high"
    elif any(word in text_lower for word in medium_keywords):
        return "medium"
    else:
        return "low"

def assign_eta(priority):
    if priority == "high":
        return random.randint(1, 2)
    elif priority == "medium":
        return random.randint(3, 5)
    else:
        return random.randint(5, 10)

def generate_dataset(n_samples=1000):

    data = []

    for _ in range(n_samples):

        category = random.choice(list(categories.keys()))
        text = random.choice(categories[category])

        priority = assign_priority(text)
        eta_days = assign_eta(priority)

        data.append({
            "text": text,
            "category": category,
            "priority": priority,
            "eta_days": eta_days
        })

    df = pd.DataFrame(data)
    df.to_csv("training_data.csv", index=False)

    print("Dataset generated successfully!")

if __name__ == "__main__":
    generate_dataset(2000)