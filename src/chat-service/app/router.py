from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import httpx
from app.models import ChatRequest, ChatResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

AUTH_SERVICE_URL = "http://auth-service/auth/users/me"
OLLAMA_SERVICE_URL = "http://ollama-service:11434/api/generate"

async def verify_token(request: Request):
    token = await oauth2_scheme(request)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(AUTH_SERVICE_URL, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return response.json()

@router.post("/", response_model=ChatResponse)
async def chat_with_llm(chat_request: ChatRequest, user=Depends(verify_token)):
    payload = {
        "model": chat_request.model,
        "prompt": chat_request.message,
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(OLLAMA_SERVICE_URL, json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Failed to query LLM")
    data = resp.json()
    return ChatResponse(
        response=data.get("response", ""),
        session_id=chat_request.session_id,
        model=chat_request.model
    )