from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    conversation_id: Optional[str] = None


class RetrievedDoc(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class ChatResponse(BaseModel):
    reply: str
    used_docs: Optional[List[RetrievedDoc]] = None
