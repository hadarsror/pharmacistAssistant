import streamlit as st
import requests
import json
from app.database import USERS_DB

st.set_page_config(page_title="Wonderful Pharmacy Assistant", page_icon="💊")

st.title("💊 Pharmacy AI Assistant")
st.caption("Enterprise-grade Agentic Pharmacist - Hadar's Home Assignment")

# Sidebar: Dynamically pull all IDs from the database
user_ids = ["Select an ID..."] + list(USERS_DB.keys())
user_id_selection = st.sidebar.selectbox("Select User ID", user_ids, index=0)

if user_id_selection == "Select an ID...":
    # Pass no session_id to the backend or a placeholder
    session_id = "default"
else:
    session_id = user_id_selection

# Clear chat if the user ID changes
if "last_user_id" not in st.session_state:
    st.session_state.last_user_id = session_id

if st.session_state.last_user_id != session_id:
    st.session_state.messages = []
    st.session_state.last_user_id = session_id
    st.rerun()
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("How can I help you with your medication?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Call the FastAPI backend
        # Note: Ensure FastAPI is running on port 8000
        url = f"http://localhost:8000/chat?user_input={prompt}&session_id={session_id}"

        with requests.post(url, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data = json.loads(decoded_line[6:])

                        # Handle Tool Call visualization (Requirement #4)
                        if "tool" in data:
                            with st.status("Verifying pharmacy records...",
                                           expanded=False):
                                st.write(f"Querying: {data['tool']}")

                        # Handle Text Content
                        if "content" in data:
                            full_response += data["content"]
                            response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
