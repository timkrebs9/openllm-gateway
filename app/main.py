from fastapi import FastAPI
from app.routers.chat import router as chat_router

app = FastAPI(title="LLM API Hub via Ollama")

app.include_router(chat_router, prefix="/chat", tags=["chat"])
