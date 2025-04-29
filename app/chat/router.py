import logging
import os
from typing import List, Dict

import httpx
from fastapi import APIRouter, HTTPException, Depends, status
from dotenv import load_dotenv

from app.chat.models import ChatRequest, ChatResponse
from app.auth.router import get_current_user # Assuming a function to get validated user info

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration - Use environment variables
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL") # Example K8s service name

# In-memory storage for session data (Replace with Redis/DB in production)
# Warning: This is not suitable for multi-replica deployments in K8s
session_data: Dict[str, List[Dict[str, str]]] = {}

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    # current_user: dict = Depends(get_current_user) # Re-enable when auth is implemented
):
    """
    Handles chat requests, maintains session history (in-memory),
    and interacts with the Ollama API.
    """
    # logger.info(f"Chat request received for session {request.session_id} by user {current_user.get('username')}") # Use when auth is ready
    logger.info(f"Chat request received for session {request.session_id} with model {request.model}")

    session_id = request.session_id
    if session_id not in session_data:
        logger.info(f"Creating new session: {session_id}")
        session_data[session_id] = []

    # Append user message to history
    session_data[session_id].append({"role": "user", "content": request.message})

    payload = {
        "model": "gemma3:1b",
        "messages": session_data[session_id],
        "stream": False # Keep it simple for now
    }

    logger.debug(f"Sending payload to Ollama ({OLLAMA_API_URL}): {payload}")

    async with httpx.AsyncClient(timeout=60.0) as client: # Increased timeout
        try:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx
            data = response.json()
            logger.debug(f"Received response from Ollama: {data}")

            # Extract the actual message content
            ollama_response_content = data.get("message", {}).get("content", "")
            if not ollama_response_content:
                 logger.warning("Ollama response content is empty.")
                 # Handle cases where the response might be structured differently or empty
                 ollama_response_content = data.get("response", "") # Fallback for older Ollama versions?

            # Append assistant response to history
            session_data[session_id].append({"role": "assistant", "content": ollama_response_content})

            # Limit history size (e.g., keep last 10 messages) - Simple approach
            max_history = 10
            if len(session_data[session_id]) > max_history:
                 logger.debug(f"Trimming session history for {session_id}")
                 # Keep the first system message (if any) and the last N messages
                 # This needs a more robust implementation depending on needs
                 session_data[session_id] = session_data[session_id][-max_history:]


            return ChatResponse(
                response=ollama_response_content,
                session_id=session_id,
                model=request.model
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while contacting Ollama: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Ollama service error: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Network error occurred while contacting Ollama: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to Ollama service: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred in chat endpoint for session {session_id}") # Log full traceback
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred: {str(e)}")

@router.get("/history/{session_id}", response_model=List[Dict[str, str]])
async def get_session_history(session_id: str):
    """
    Retrieves the chat history for a given session ID.
    """
    if session_id not in session_data:
        logger.warning(f"Session history requested for non-existent session: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    logger.info(f"Retrieving history for session: {session_id}")
    return session_data[session_id]
