from fastapi import FastAPI
from app.routers.chat import router as chat_router
import os # Import os

app = FastAPI(title="LLM API Hub via Ollama - Deepseek")

# Simple root endpoint
@app.get("/")
async def root():
    # Display the configured Ollama endpoint (optional, for debugging)
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "Not Set")
    return {"message": "LLM API Hub running", "ollama_endpoint": ollama_endpoint}

app.include_router(chat_router, prefix="/chat", tags=["chat"])
