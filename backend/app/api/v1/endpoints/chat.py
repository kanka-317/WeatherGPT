from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.chat import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.services.llm_service import LLMService

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a conversational message to WeatherGPT with tool-calling",
)
async def chat_message(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Conversational endpoint executing tool-calling to fetch live weather,
    multi-day forecasts, and active alerts before producing a grounded response.
    """
    service = LLMService(db=db)
    return await service.chat(
        message=payload.message,
        session_id=payload.session_id,
        lat=payload.lat,
        lon=payload.lon,
        language=payload.language or "en",
    )


@router.get(
    "/history",
    response_model=List[ChatMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve session chat message history",
)
async def get_chat_history(
    session_id: str = Query(..., description="Active chat session identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[ChatMessageResponse]:
    """Retrieve full conversation history for a given session_id."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [ChatMessageResponse.model_validate(m) for m in messages]
