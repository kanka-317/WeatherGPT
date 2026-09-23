from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or statement")
    session_id: str = Field(..., min_length=1, description="Client session identifier")
    lat: Optional[float] = Field(default=None, description="Optional user latitude override")
    lon: Optional[float] = Field(default=None, description="Optional user longitude override")
    language: Optional[str] = Field(default="en", description="Target response language (en, hi, bn)")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Assistant's grounded response")
    session_id: str = Field(..., description="Active session ID")
    language: str = Field(default="en", description="Response language code")
    tools_called: List[str] = Field(default_factory=list, description="Names of tools invoked during response generation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    tool_calls: Optional[Any] = None
    tool_call_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
