import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Complaint Routing", layout="centered")

st.title("🚀 AI Complaint Auto-Routing System")

st.markdown("Submit your complaint below:")

user_id = st.text_input("User ID")
text = st.text_area("Complaint Text")
language = st.selectbox("Language", ["english", "hindi"])
location = st.text_input("Location")
category = st.text_input("Category")

if st.button("Submit Complaint"):

    if not text:
        st.error("Please enter complaint text.")
    else:
        payload = {
            "user_id": user_id,
            "text": text,
            "language": language,
            "location": location,
            "category": category
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/submit-complaint",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                st.success("Complaint Processed Successfully!")

                st.write("### 🧑 Assigned Officer")
                st.write(result["assigned_officer"])
                st.write("Department:", result["department"])

                st.write("### ⚡ Priority")
                st.write(result["priority"])

                st.write("### ⏳ Estimated Resolution Time")
                st.write(f"{result['predicted_eta_days']} days")

                st.write("### 🔍 Similar Complaints")
                if result["similar_complaints"]:
                    for cid in result["similar_complaints"]:
                        st.write("-", cid)
                else:
                    st.write("No similar complaints found.")

            else:
                st.error("Backend Error")

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")