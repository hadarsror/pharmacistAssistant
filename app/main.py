import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.agent import SYSTEM_PROMPT, TOOLS, get_medication_info, \
    check_user_status, get_alternatives


load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

# MAPPING TOOLS
TOOL_MAP = {
    "get_medication_info": get_medication_info,
    "check_user_status": check_user_status,
    "get_alternatives": get_alternatives  # Add this line
}

# SIMPLE IN-MEMORY SESSION STORE
# In a real app, this would be Redis. Here, it provides "Memory".
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
        # Add Assistant tool call message to history
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

        # Execute tools and add results
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

        # Recursive call with updated history
        async for next_chunk in agent_loop(messages):
            yield next_chunk
    else:
        # Save the final assistant response to history
        messages.append({"role": "assistant", "content": current_content})


@app.post("/chat")
async def chat(user_input: str, session_id: str = "default"):
    if session_id not in chat_sessions:
        # Only inject the ID if it's not the default placeholder
        auth_context = ""
        if session_id != "default":
            auth_context = f"\n\nCURRENT_USER_ID: {session_id}"

        chat_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT + auth_context}
        ]

    # Append the new user message to the history
    chat_sessions[session_id].append({"role": "user", "content": user_input})

    return StreamingResponse(
        agent_loop(chat_sessions[session_id]),
        media_type="text/event-stream"
    )