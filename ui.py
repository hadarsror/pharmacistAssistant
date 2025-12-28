import streamlit as st
import requests
import json

st.set_page_config(page_title="Wonderful Pharmacy Assistant", page_icon="💊")

st.title("💊 Pharmacy AI Assistant")
st.caption("Enterprise-grade Agentic Pharmacist - Hadar's Home Assignment")

# Sidebar for user selection to simulate "Logged in" state
user_id = st.sidebar.selectbox("Select User ID", ["312456789", "204567891", "300987654", "201234567"])

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
        url = f"http://localhost:8000/chat?user_input={prompt}&session_id={user_id}"

        with requests.post(url, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data = json.loads(decoded_line[6:])

                        # Handle Tool Call visualization (Requirement #4)
                        if "tool" in data:
                            with st.status(f"Running Tool: {data['tool']}...",
                                           expanded=False):
                                st.write(f"Arguments: {data['args']}")

                        # Handle Text Content
                        if "content" in data:
                            full_response += data["content"]
                            response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})