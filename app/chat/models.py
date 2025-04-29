from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: str = "deepseek-coder:6.7b" # Default model

class ChatResponse(BaseModel):
    response: str
    session_id: str
    model: str
