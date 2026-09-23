from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)  # user, assistant, system, tool
    content = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True)  # Stored JSON list of tool calls
    tool_call_id = Column(String(100), nullable=True)  # Linked tool_call_id when role == 'tool'
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("idx_chat_session_time", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}', role='{self.role}')>"
