# Pharmacy Assistant Agent
An AI pharmacy assistant that helps users check their medications, find alternatives, and review their prescriptions. It handles basic pharmacy queries in both English and Hebrew, checks for allergies, and makes sure users don't accidentally take something they shouldn't. Uses OpenAI's function calling to pull data from a mock pharmacy database with patient records and medication inventory.

The main thing here is safety checks - it'll flag if you're allergic to something or if there's a conflict between your prescriptions and allergies. Works through a simple chat interface and keeps conversations focused on one medication at a time so there's no confusion.


## Features

### Core Capabilities
- Checks if you're allowed to take a specific medication (based on your prescriptions)

- Spots allergy conflicts before you take something dangerous

- Shows what's actually in stock at the pharmacy

- Finds alternative meds with the same active ingredient

- Pulls up your full prescription list and medical history

- Works in both English and Hebrew - responds in whatever language you use

### Safety Features
- Flags critical allergy alerts if you're allergic to what you're asking about

- Catches prescription conflicts (like when your doc prescribed something you're allergic to)

- Won't give medical advice - just shows factual info from the database

- Always adds a disclaimer to check with your doctor or pharmacist for actual medical guidance

- Resets context between medications so old allergy warnings don't bleed into new queries

### Technical Features
- Uses OpenAI function calling to query a mock pharmacy database

- Bilingual prompt engineering handles English/Hebrew switching mid-conversation

- FastAPI backend with a simple Gradio chat UI

- Stateless design - each medication query is independent

- Docker support for easy deployment

## Architecture

Pretty simple setup - FastAPI backend talks to OpenAI, Streamlit for the chat UI:

**Flow:**
1. User types a message in Streamlit UI (English or Hebrew)
2. UI sends it to FastAPI `/chat` endpoint with their user ID
3. FastAPI maintains the conversation history and calls OpenAI's API
4. GPT-5 reads the system prompt and decides if it needs to call any tools
5. If tools are needed (like checking allergies), FastAPI runs them against the mock database
6. Results go back to GPT, which formats a response
7. Response streams back to the UI in real-time

**Main files:**
- `main.py` - FastAPI server, handles streaming and tool execution
- `agent.py` - The system prompt that tells GPT how to behave
- `tools.py` - Four functions that query the database (check_user_status, get_patient_details, etc)
- `tool_schemas.py` - JSON schemas so GPT knows what each tool does
- `database.py` - Mock patient and medication data (just Python dicts)
- `ui.py` - Streamlit chat interface with right-to-left text support for Hebrew

Sessions are stored in-memory on the backend (keyed by user ID), so they persist across messages in the same session. If you switch users in the UI dropdown or refresh the page, Streamlit clears its local history. The backend keeps its version until the server restarts.



## Prerequisites
- Docker installed on your machine
- OpenAI API key


## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/hadarsror/pharmacistAssistant.git
cd pharmacistAssistant
```

### 2. Create a `.env` file with your OpenAI key (see .env.example):
```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Build and run:
```bash
docker build -t pharmacy-assistant .
docker run -p 8000:8000 -p 8501:8501 --env-file .env pharmacy-assistant
```

### 4. Open your browser to `http://localhost:8501` for the chat UI
The backend API runs on port 8000, but you'll interact with the Streamlit interface on 8501.


## API Documentation

### Tool Functions
The agent can call these four tools based on user queries:

- **check_user_status** - Checks if user has prescription, verifies allergies, shows stock
- **get_patient_details** - Retrieves full patient profile (prescriptions, medical history, allergies)
- **get_medication_info** - Gets medication facts (ingredients, restrictions, stock)
- **get_alternatives** - Finds meds with the same active ingredient

**Built with:**
- Python 3.11
- FastAPI - backend API
- Streamlit - chat UI
- OpenAI GPT-5 - agent logic
- Uvicorn - ASGI server
