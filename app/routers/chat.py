from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from app.services.ollama_client import query_ollama

router = APIRouter()

class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str

class ChatRequest(BaseModel):
    model: Literal["llama3", "mistral", "gemma"]
    messages: List[Message]

@router.post("/")
async def chat(request: ChatRequest):
    try:
        response = await query_ollama(request.model, request.messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
