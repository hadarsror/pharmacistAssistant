import streamlit as st
import requests
import json
import re
from app.database import USERS_DB

st.set_page_config(page_title="Wonderful Pharmacy Assistant", page_icon="💊")

st.title("💊 Pharmacy AI Assistant")
st.caption("Enterprise-grade Agentic Pharmacist")


# --- HELPER: Python-based Direction Detection ---
def get_direction(text):
    """Returns 'rtl' if the text contains Hebrew characters, otherwise 'ltr'."""
    if text and re.search(r'[\u0590-\u05FF]', text):
        return "rtl"
    return "ltr"


def get_alignment(direction):
    return "right" if direction == "rtl" else "left"


# --- SIDEBAR & SESSION ---
user_ids = ["Select an ID..."] + list(USERS_DB.keys())
user_id_selection = st.sidebar.selectbox("Select User ID", user_ids, index=0)

# IF sidebar is "Select an ID...", we send "default" to backend.
# The backend/agent will then see "default" and trigger the "Ask for ID" protocol.
session_id = "default" if user_id_selection == "Select an ID..." else user_id_selection

if "last_user_id" not in st.session_state:
    st.session_state.last_user_id = session_id

if st.session_state.last_user_id != session_id:
    st.session_state.messages = []
    st.session_state.last_user_id = session_id
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Calculate direction for THIS specific message
        msg_dir = get_direction(message["content"])
        msg_align = get_alignment(msg_dir)

        st.markdown(
            f'<div style="direction: {msg_dir}; text-align: {msg_align};">{message["content"]}</div>',
            unsafe_allow_html=True
        )

# --- MAIN CHAT LOGIC ---
if prompt := st.chat_input("How can I help you with your medication?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        # Detect direction for user input
        user_dir = get_direction(prompt)
        st.markdown(
            f'<div style="direction: {user_dir}; text-align: {get_alignment(user_dir)};">{prompt}</div>',
            unsafe_allow_html=True
        )

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Status box (created once)
        status_container = st.status("Processing request...", expanded=True)

        url = f"http://localhost:8000/chat?user_input={prompt}&session_id={session_id}"

        try:
            with requests.post(url, stream=True) as r:
                r.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)
                
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data = json.loads(decoded_line[6:])

                            if "tool" in data:
                                status_container.write(
                                    f"Using tool: {data['tool']}")

                            if "content" in data:
                                status_container.update(
                                    label="Response generated",
                                    state="complete", expanded=False)
                                full_response += data["content"]

                                # Real-time direction detection for streaming text
                                curr_dir = get_direction(full_response)
                                response_placeholder.markdown(
                                    f'<div style="direction: {curr_dir}; text-align: {get_alignment(curr_dir)};">{full_response}▌</div>',
                                    unsafe_allow_html=True
                                )

            # Final render
            final_dir = get_direction(full_response)
            response_placeholder.markdown(
                f'<div style="direction: {final_dir}; text-align: {get_alignment(final_dir)};">{full_response}</div>',
                unsafe_allow_html=True
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except requests.exceptions.HTTPError as e:
            status_container.update(label="Request Error", state="error")
            if e.response.status_code == 400:
                # Try multiple ways to extract error detail
                error_detail = 'Bad request'
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', error_data)
                except:
                    try:
                        error_detail = e.response.text
                    except:
                        pass
                
                # Provide helpful context for input length errors
                if "too long" in str(error_detail).lower() or len(prompt) > 1000:
                    st.error(f"❌ Your message is too long!\n\n**Your message:** {len(prompt)} characters\n**Maximum allowed:** 1000 characters\n\nPlease shorten your message and try again.")
                else:
                    st.error(f"❌ {error_detail}")
            else:
                st.error(f"❌ Server error ({e.response.status_code}): {e}")
        except Exception as e:
            status_container.update(label="Connection Error", state="error")
            st.error(f"❌ Error connecting to backend: {e}")