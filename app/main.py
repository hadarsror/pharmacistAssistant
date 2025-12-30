"""
FastAPI backend for the pharmacy assistant agent.
Handles streaming chat interactions with OpenAI GPT-5.
"""

import os
import json
import re
import logging
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from dotenv import load_dotenv

from app.agent import SYSTEM_PROMPT
from app.tool_schemas import TOOLS
from app.tools import (
    get_patient_details,
    get_medication_info,
    check_user_status,
    get_alternatives
)
from app.database import USERS_DB

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MAX_INPUT_LENGTH = 1000
MAX_MESSAGES_PER_SESSION = 50
MAX_SESSIONS = 100

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = AsyncOpenAI(api_key=api_key)
app = FastAPI(title="Pharmacy Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool function mapping
TOOL_MAP = {
    "get_medication_info": get_medication_info,
    "check_user_status": check_user_status,
    "get_alternatives": get_alternatives,
    "get_patient_details": get_patient_details
}

# In-memory session store
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}


def ensure_disclaimer(response: str, session_id: str) -> str:
    """
    Ensure all responses contain appropriate disclaimer.
    
    Args:
        response: The agent's response text
        session_id: Session ID to determine language context
        
    Returns:
        Response with disclaimer appended if missing
    """
    disclaimer_en = "This information is for reference only. For medical advice, please consult your doctor or pharmacist."
    disclaimer_he = "מידע זה למטרות התייחסות בלבד. לייעוץ רפואי, אנא היוועצו עם הרופא או הרוקח שלכם."
    
    # Check if response is in Hebrew (simple heuristic: contains Hebrew characters)
    is_hebrew = bool(re.search(r'[\u0590-\u05FF]', response))
    
    disclaimer = disclaimer_he if is_hebrew else disclaimer_en
    
    # Only add if not already present
    if disclaimer not in response and response.strip():
        return response + "\n\n" + disclaimer
    return response


def cleanup_old_sessions():
    """
    Remove oldest sessions if limit exceeded.
    Keeps system from running out of memory.
    """
    if len(chat_sessions) > MAX_SESSIONS:
        # Remove oldest 20% of sessions
        sessions_to_remove = list(chat_sessions.keys())[:MAX_SESSIONS // 5]
        for session_id in sessions_to_remove:
            del chat_sessions[session_id]
            logger.info(f"Removed old session: {session_id}")


async def execute_tool_call(tool_name: str, args: Dict[str, Any]) -> Dict[
    str, Any]:
    """
    Execute a single tool call with error handling.

    Args:
        tool_name: Name of the tool to execute
        args: Arguments to pass to the tool

    Returns:
        Tool execution result or error dictionary
    """
    try:
        logger.info(f"Executing tool: {tool_name} with args: {args}")
        result = await asyncio.to_thread(TOOL_MAP[tool_name], **args)
        logger.info(f"Tool {tool_name} returned: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}",
                     exc_info=True)
        return {"error": f"Tool execution failed: {str(e)}"}


async def agent_loop(messages: List[Dict[str, Any]]):
    """
    Main agent loop that handles streaming responses and tool calls.
    Implements parallel tool execution for better performance.

    Args:
        messages: Conversation history

    Yields:
        Server-sent events containing content chunks and tool call notifications
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            tools=TOOLS,
            stream=True
        )

        tool_calls = []
        current_content = ""

        # Stream response and collect tool calls
        async for chunk in response:
            delta = chunk.choices[0].delta

            if delta.content:
                current_content += delta.content
                yield f"data: {json.dumps({'content': delta.content})}\n\n"

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if len(tool_calls) <= tc.index:
                        tool_calls.append({
                            "id": tc.id,
                            "name": tc.function.name,
                            "args": ""
                        })
                    if tc.function.arguments:
                        tool_calls[tc.index]["args"] += tc.function.arguments

        # Process tool calls if any
        if tool_calls:
            assistant_msg = {
                "role": "assistant",
                "content": current_content,
                "tool_calls": [
                    {
                        "id": t["id"],
                        "type": "function",
                        "function": {"name": t["name"], "arguments": t["args"]}
                    }
                    for t in tool_calls
                ]
            }
            messages.append(assistant_msg)

            # Execute tools in parallel for better performance
            tool_results = await asyncio.gather(*[
                execute_tool_call(t["name"], json.loads(t["args"]))
                for t in tool_calls
            ])

            # Add tool results to messages and notify UI
            for tool_call, result in zip(tool_calls, tool_results):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
                yield f"data: {json.dumps({'tool': tool_call['name'], 'args': json.loads(tool_call['args'])})}\n\n"

            # Recursive call to get final response
            async for next_chunk in agent_loop(messages):
                yield next_chunk
        else:
            # No tool calls, final response
            messages.append({"role": "assistant", "content": current_content})

    except Exception as e:
        logger.error(f"Error in agent loop: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post("/chat")
async def chat(user_input: str, session_id: str = "default"):
    """
    Handle chat requests with streaming responses.

    Args:
        user_input: User's message
        session_id: Session identifier (use patient ID for authenticated sessions)

    Returns:
        Streaming response with server-sent events
    """
    # Input validation
    if not user_input or not user_input.strip():
        raise HTTPException(status_code=400,
                            detail="user_input cannot be empty")
    
    user_input = user_input.strip()
    
    if len(user_input) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Input too long (max {MAX_INPUT_LENGTH} characters)"
        )

    logger.info(
        f"Chat request - session_id: {session_id}, input: {user_input[:100]}")

    # Cleanup old sessions periodically
    cleanup_old_sessions()

    # Initialize session with context injection
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Inject user context ONCE at session start if valid patient ID
        if session_id in USERS_DB:
            chat_sessions[session_id].append({
                "role": "system",
                "content": f"CONTEXT UPDATE: CURRENT_USER_ID is {session_id}. Patient is authenticated."
            })
            logger.info(f"User context injected for new session: {session_id}")

    # Limit session history to prevent memory issues
    if len(chat_sessions[session_id]) > MAX_MESSAGES_PER_SESSION:
        # Keep system prompt + context + last N messages
        system_messages = [msg for msg in chat_sessions[session_id] if msg["role"] == "system"]
        recent_messages = chat_sessions[session_id][-MAX_MESSAGES_PER_SESSION:]
        chat_sessions[session_id] = system_messages + recent_messages
        logger.info(f"Session {session_id} history trimmed to {len(chat_sessions[session_id])} messages")

    # Add user message to persistent session
    user_msg = {"role": "user", "content": user_input}
    chat_sessions[session_id].append(user_msg)

    # Use session history directly (no copy needed)
    return StreamingResponse(
        agent_loop(chat_sessions[session_id]),
        media_type="text/event-stream"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pharmacy-assistant"}


@app.get("/sessions")
async def list_sessions():
    """List active session IDs (for debugging)."""
    return {"active_sessions": list(chat_sessions.keys())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
