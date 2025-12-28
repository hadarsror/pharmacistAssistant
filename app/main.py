import os
import json
import re
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from dotenv import load_dotenv
# Make sure to import get_patient_details here
from app.agent import SYSTEM_PROMPT, TOOLS, get_medication_info, \
    check_user_status, get_alternatives, get_patient_details
from app.database import USERS_DB

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

# MAPPING TOOLS
TOOL_MAP = {
    "get_medication_info": get_medication_info,
    "check_user_status": check_user_status,
    "get_alternatives": get_alternatives,
    "get_patient_details": get_patient_details  # <--- Registered here
}

# SIMPLE IN-MEMORY SESSION STORE
chat_sessions = {}

async def agent_loop(messages):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        stream=True
    )

    tool_calls = []
    current_content = ""

    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            current_content += delta.content
            yield f"data: {json.dumps({'content': delta.content})}\n\n"

        if delta.tool_calls:
            for tc in delta.tool_calls:
                if len(tool_calls) <= tc.index:
                    tool_calls.append(
                        {"id": tc.id, "name": tc.function.name, "args": ""})
                if tc.function.arguments:
                    tool_calls[tc.index]["args"] += tc.function.arguments

    if tool_calls:
        assistant_msg = {
            "role": "assistant",
            "content": current_content,
            "tool_calls": [
                {"id": t["id"], "type": "function",
                 "function": {"name": t["name"], "arguments": t["args"]}}
                for t in tool_calls
            ]
        }
        messages.append(assistant_msg)

        # Execute tools
        for t in tool_calls:
            try:
                args = json.loads(t["args"])
                result = TOOL_MAP[t["name"]](**args)
                messages.append({"role": "tool", "tool_call_id": t["id"],
                                 "content": json.dumps(result)})
                yield f"data: {json.dumps({'tool': t['name'], 'args': args})}\n\n"
            except Exception as e:
                messages.append({"role": "tool", "tool_call_id": t["id"],
                                 "content": json.dumps({"error": str(e)})})

        # Recursive call
        async for next_chunk in agent_loop(messages):
            yield next_chunk
    else:
        messages.append({"role": "assistant", "content": current_content})


@app.post("/chat")
async def chat(user_input: str, session_id: str = "default"):
    # 1. Initialize Session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # 2. CONTEXT INJECTION FOR SIDEBAR
    # We copy the history to avoid permanently polluting the session with duplicate system messages
    messages_to_send = chat_sessions[session_id].copy()

    # If the Sidebar ID is valid (exists in DB), inject it
    if session_id in USERS_DB:
        messages_to_send.append({
            "role": "system",
            "content": f"CONTEXT UPDATE: CURRENT_USER_ID is {session_id}. The user is verified."
        })
    else:
        # If user typed ID manually in chat (fallback for 'default' session)
        if match := re.search(r"\b\d{9}\b", user_input):
            potential_id = match.group(0)
            if potential_id in USERS_DB:
                messages_to_send.append({
                    "role": "system",
                    "content": f"CONTEXT UPDATE: CURRENT_USER_ID is {potential_id}."
                })

    # 3. Add User Message
    user_msg = {"role": "user", "content": user_input}
    chat_sessions[session_id].append(user_msg)  # Save to long-term memory
    messages_to_send.append(user_msg)           # Send to API

    return StreamingResponse(
        agent_loop(messages_to_send),
        media_type="text/event-stream"
    )