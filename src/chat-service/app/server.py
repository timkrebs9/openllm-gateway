from fastapi import FastAPI
from app.router import router

app = FastAPI(title="Chat Service")

app.include_router(router, prefix="/chat", tags=["Chat"])