import json
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.db.base import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_event_user_ts", "user_id", "timestamp"),
    )

    @classmethod
    def log(cls, db: Session, user_id: int, event_type: str, payload: dict = None):
        entry = cls(user_id=user_id, event_type=event_type, payload=json.dumps(payload or {}))
        db.add(entry)
        db.commit()
        return entry

    @classmethod
    def get_recent(cls, db: Session, user_id: int, days: int = 7):
        since = datetime.utcnow() - timedelta(days=days)
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.timestamp >= since)
            .order_by(cls.timestamp.desc())
            .all()
        )
