import httpx
from typing import List
from app.routers.chat import Message

OLLAMA_BASE_URLS = {
    "llama3": "http://ollama-llama3:11434",
    "mistral": "http://ollama-mistral:11434",
    "gemma": "http://ollama-gemma:11434",
}

async def query_ollama(model: str, messages: List[Message]) -> str:
    url = f"{OLLAMA_BASE_URLS[model]}/api/chat"
    payload = {
        "model": model,
        "messages": [m.dict() for m in messages],
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")
