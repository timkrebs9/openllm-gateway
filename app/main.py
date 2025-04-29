import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers from submodules
from app.chat.router import router as chat_router
from app.auth.router import router as auth_router, oauth2_scheme # Import oauth2_scheme from auth

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="OpenLLM Gateway")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/", tags=["Root"])
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the OpenLLM Gateway API"}

# Note: The original main.py had session_data and OLLAMA constants.
# session_data is moved to app/chat/router.py (consider a shared cache/DB later).
# OLLAMA_API_URL should ideally be configured via environment variables.
# oauth2_scheme is now defined and managed within app/auth/router.py but imported here
# for potential cross-module use if needed, though dependencies should ideally flow one way.