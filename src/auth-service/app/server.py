from fastapi import FastAPI
from app.router import router

app = FastAPI(title="Authentication Service")

app.include_router(router, prefix="/auth", tags=["Authentication"])
