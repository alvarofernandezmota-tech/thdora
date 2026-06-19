import json
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.db.base import Base


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    notes = Column(Text, default="")
    tags = Column(Text, default="[]")
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_mood_user_ts", "user_id", "timestamp"),
    )

    @classmethod
    def get_recent(cls, db: Session, user_id: int, days: int = 30):
        since = datetime.utcnow() - timedelta(days=days)
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.timestamp >= since)
            .order_by(cls.timestamp.desc())
            .all()
        )

    def get_tags(self) -> list:
        try:
            return json.loads(self.tags)
        except Exception:
            return []
