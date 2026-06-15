from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.api.deps import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_id = Column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_conversation_user_timestamp", "user_id", "timestamp"),
    )

    @classmethod
    def get_history(cls, db: Session, user_id: int, limit: int = 10) -> list[dict]:
        rows = (
            db.query(cls)
            .filter(cls.user_id == user_id)
            .order_by(cls.timestamp.desc())
            .limit(limit)
            .all()
        )
        rows.reverse()
        return [{"role": r.role, "content": r.content} for r in rows]

    @classmethod
    def save(
        cls,
        db: Session,
        user_id: int,
        role: str,
        content: str,
        session_id: str | None = None,
    ) -> "Conversation":
        entry = cls(
            user_id=user_id,
            role=role,
            content=content,
            session_id=session_id,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
