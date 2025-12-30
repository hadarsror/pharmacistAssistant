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
- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- Internet connection for API calls


## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/hadarsror/pharmacistAssistant.git
cd pharmacistAssistant
```

### 2. Create Virtual Environment
```bash

```

### 3. Install Dependencies
```bash
[Installation commands]
```

### 4. Configure Environment Variables
```bash
[Environment setup]
```

## Running the Application

### Option 1: Local Development

[Instructions for running locally]

### Option 2: Docker Deployment

[Instructions for Docker]

## Usage Guide


### Example Interactions

**1. Check Medication Availability (Flow 1)**
```
[Example]
```

**2. Find Alternatives (Flow 2)**
```
[Example]
```

**3. Review Prescriptions (Flow 3)**
```
[Example]
```

### Safety Policies

[List policies]

## Testing

### Test Coverage
[Describe test coverage]

### Manual Testing Checklist
- [ ] [Test items]

### Running Tests
```bash
[Test commands]
```

## API Documentation

### Endpoints


### Tool Functions


## Configuration

### Environment Variables
[List variables]


## Project Structure Details

### Backend (`app/`)
[Describe backend files]

### Frontend
[Describe frontend]

### Documentation
[Describe docs]


**Built with:**
- [Technologies used]
