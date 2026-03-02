import streamlit as st
import requests
import pandas as pd
import base64
import jwt

API_BASE = "http://127.0.0.1:8001"

st.set_page_config(page_title="AI Complaint Routing", layout="wide")


# BACKGROUND IMAGE
def add_bg(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}

        .block-container {{
            background: rgba(0,0,0,0.75);
            padding: 2rem;
            border-radius: 15px;
        }}

        h1,h2,h3,label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg("assets/background.png")


# SESSION STATE
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

# REGISTER
def register_page():
    st.title("📝 Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    flat_number = st.text_input("Flat Number")

    if st.button("Register"):
        response = requests.post(
            f"{API_BASE}/register",
            json={
                "name": name,
                "email": email,
                "password": password,
                "flat_number": flat_number
            }
        )

        if response.status_code == 200:
            st.success("Account created successfully. Please login.")
        else:
            st.error(response.text)

# LOGIN
def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{API_BASE}/login",
            data={
                "username": email,
                "password": password
            }
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state.token = token

            decoded = jwt.decode(token, options={"verify_signature": False})
            st.session_state.role = decoded.get("role")

            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# SUBMIT COMPLAINT
def submit_complaint_page():

    st.title("📨 Submit New Complaint")
    st.markdown("---")

    location = st.text_input("📍 Location / Area")
    text_input = st.text_area("📝 Complaint Description (Optional if recording)")

    st.markdown("### 🎙 Record Audio Complaint")
    audio_data = st.audio_input("Tap to Record")

    if st.button("🚀 Submit Complaint"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        params = {
            "location": location,
            "text": text_input
        }

        files = None

        if audio_data:
            files = {
                "file": (
                    "recording.wav",
                    audio_data,
                    "audio/wav"
                )
            }

        response = requests.post(
            f"{API_BASE}/submit-complaint",
            headers=headers,
            params=params,
            files=files
        )

        if response.status_code == 200:
            result = response.json()

            st.success("Complaint Submitted Successfully!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Priority", result["priority"])
            col2.metric("Predicted ETA (Days)", result["predicted_eta_days"])
            col3.metric("Assigned Officer", result["assigned_officer"])

            st.markdown("---")
            st.subheader("📝 Transcribed Text")
            st.write(result["transcribed_text"])

            st.markdown("---")
            st.subheader("🔎 Similar Complaints")
            st.write(result["similar_complaints"])

        else:
            st.error(f"Error {response.status_code}")
            st.write(response.text)

# VIEW COMPLAINTS
def view_complaints():

    st.title("📋 Complaints")

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    response = requests.get(
        f"{API_BASE}/complaints",
        headers=headers
    )

    if response.status_code != 200:
        st.error("Unable to fetch complaints")
        st.write(response.text)
        return

    complaints = response.json()

    if not complaints:
        st.info("No complaints found.")
        return

    # ==========================
    # ADMIN VIEW
    # ==========================
    if st.session_state.role == "admin":

        users = {}

        for c in complaints:
            key = f"{c.get('user_name', 'Unknown')} ({c.get('flat_number', 'N/A')})"
            if key not in users:
                users[key] = []
            users[key].append(c)

        for user, user_complaints in users.items():

            st.markdown(f"## 👤 {user}")
            st.markdown("---")

            for c in user_complaints:

                st.write(f"**Complaint ID:** {c['id']}")
                st.write(f"**Location:** {c['location']}")
                st.write(f"**Text:** {c['text']}")
                st.write(f"**Status:** {c['status']}")

                # Only allow resolve if pending
                if c["status"] == "pending":

                    actual_priority = st.selectbox(
                        "Actual Priority",
                        ["low", "medium", "high"],
                        key=f"priority_{c['id']}"
                    )

                    resolution_days = st.number_input(
                        "Resolution Days",
                        min_value=0.0,
                        step=0.5,
                        key=f"days_{c['id']}"
                    )

                    if st.button("Resolve Complaint", key=f"resolve_{c['id']}"):

                        resolve_response = requests.put(
                            f"{API_BASE}/resolve-complaint/{c['id']}",
                            headers=headers,
                            params={
                                "actual_priority": actual_priority,
                                "actual_resolution_days": resolution_days
                            }
                        )

                        if resolve_response.status_code == 200:
                            st.success("Complaint Resolved Successfully")
                            st.rerun()
                        else:
                            st.error("Failed to resolve complaint")
                            st.write(resolve_response.text)

                else:
                    # Show resolved info
                    st.success("✅ Complaint already resolved")
                    st.write(f"Actual Priority: {c.get('actual_priority', '-')}")
                    st.write(f"Resolution Days: {c.get('actual_resolution_days', '-')}")

                st.markdown("-----")

    # ==========================
    # USER VIEW
    # ==========================
    else:

        for c in complaints:

            st.markdown("---")
            st.write(f"**Complaint ID:** {c['id']}")
            st.write(f"**Location:** {c['location']}")
            st.write(f"**Text:** {c['text']}")
            st.write(f"**Status:** {c['status']}")

            if c["status"] == "resolved":
                st.success("✅ This complaint has been resolved.")
                st.write(f"Actual Priority: {c.get('actual_priority', '-')}")
                st.write(f"Resolution Days: {c.get('actual_resolution_days', '-')}")
            else:
                st.warning("⏳ This complaint is still pending.")


# MODEL EVALUATION

def evaluation_dashboard():

    st.title("📊 Model Evaluation Dashboard")
    st.markdown("---")

    response = requests.get(
        f"{API_BASE}/evaluate-model"
    )

    if response.status_code != 200:
        st.error("Unable to fetch metrics")
        st.write(response.text)
        return

    data = response.json()

    # If no data available
    if "priority_metrics" not in data:
        st.warning(data.get("message", "No evaluation data available"))
        return

    accuracy = data["priority_metrics"]["accuracy"]
    f1 = data["priority_metrics"]["f1_score"]
    mae = data["eta_metrics"]["mae"]
    total = data["total_evaluated"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Priority Accuracy", f"{accuracy:.2%}")
    col2.metric("F1 Score", f"{f1:.2f}")
    col3.metric("ETA MAE (Days)", f"{mae:.2f}")
    col4.metric("Total Evaluated", total)

    st.markdown("---")

    # Chart
    chart_data = pd.DataFrame({
        "Metric": ["Accuracy", "F1 Score", "MAE"],
        "Value": [accuracy, f1, mae]
    })

    st.bar_chart(chart_data.set_index("Metric"))

# SIDEBAR NAVIGATION

with st.sidebar:
    st.title("🧭 Navigation")

    if st.session_state.token is None:
        page = st.radio("Go to", [
            "Login",
            "Register",
        ])
    else:
        if st.session_state.role == "admin":
            page = st.radio("Go to", [
                "All Complaints",
                "Model Evaluation",
                "Logout"
            ])
        else:
            page = st.radio("Go to", [
                "Submit Complaint",
                "My Complaints",
                "Logout"
            ])

# ROUTING

if page == "Login":
    login_page()

elif page == "Register":
    register_page()

elif page == "Submit Complaint":
    submit_complaint_page()

elif page in ["My Complaints", "All Complaints"]:
    view_complaints()

elif page == "Model Evaluation":
    evaluation_dashboard()

elif page == "Logout":
    st.session_state.token = None
    st.session_state.role = None
    st.success("Logged out")
    st.rerun()