from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_conv_user_ts", "user_id", "timestamp"),
    )

    @classmethod
    def get_recent(cls, db: Session, user_id: int, limit: int = 20):
        return (
            db.query(cls)
            .filter(cls.user_id == user_id)
            .order_by(cls.timestamp.desc())
            .limit(limit)
            .all()
        )
