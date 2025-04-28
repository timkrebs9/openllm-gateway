import httpx
import os
from typing import List, Dict, Any
from app.routers.chat import Message # Assuming Message model is in chat router
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file for local dev

# Get the Ollama service URL from environment variable
# Default to localhost if not set (for local testing)
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
TARGET_MODEL = "deepseek-r1:8b" # Define the target model

async def query_ollama(messages: List[Message]) -> str:
    """
    Sends a chat request to the Ollama API using the configured endpoint and model.
    """
    url = f"{OLLAMA_ENDPOINT}/api/chat"
    payload: Dict[str, Any] = {
        "model": TARGET_MODEL, # Use the specific model
        "messages": [m.dict() for m in messages],
        "stream": False # Keep response as a single JSON object
    }

    timeout = httpx.Timeout(300.0) # Increase timeout for potentially long LLM responses
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            print(f"Sending request to {url} with model {TARGET_MODEL}") # Debug print
            response = await client.post(url, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            response_data = response.json()
            # Extract content from the 'message' object in the response
            content = response_data.get("message", {}).get("content", "")
            if not content:
                print(f"Warning: Received empty content from Ollama. Full response: {response_data}")
            return content
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
