from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from app.services.ollama_client import query_ollama

router = APIRouter()

class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str

class ChatRequest(BaseModel):
    # Model is no longer needed here, as the backend service targets a specific model
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")
    # Ensure the last message is from the user
    if request.messages[-1].role != "user":
         raise HTTPException(status_code=400, detail="Last message must be from the 'user'.")

    try:
        # Query the specific Ollama backend instance
        response_content = await query_ollama(request.messages)
        if not response_content:
             # Handle cases where Ollama might return an empty response
             print("Warning: Ollama service returned empty content.")
             # Decide how to handle this - return empty, default message, or raise error
             # For now, return empty response:
             # return ChatResponse(response="")
             # Or raise an error:
             raise HTTPException(status_code=500, detail="LLM failed to generate a response.")

        return ChatResponse(response=response_content)
    except httpx.HTTPStatusError as e:
         # Log the error details if possible
         error_detail = f"LLM service error: {e.response.status_code}"
         try:
             error_body = e.response.json()
             error_detail += f" - {error_body.get('error', e.response.text)}"
         except Exception: # Handle cases where response is not JSON
             error_detail += f" - {e.response.text}"
         print(f"HTTPStatusError: {error_detail}") # Log error
         raise HTTPException(status_code=502, detail=error_detail) # 502 Bad Gateway might be appropriate
    except httpx.RequestError as e:
         print(f"RequestError connecting to LLM service: {e}") # Log error
         raise HTTPException(status_code=504, detail=f"Could not connect to LLM service: {e}") # 504 Gateway Timeout
    except Exception as e:
        print(f"Unhandled exception in chat endpoint: {e}") # Log error
        # Consider more specific error handling based on potential exceptions
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
