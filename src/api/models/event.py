import json
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.api.deps import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    metadata_ = Column("metadata", Text, nullable=False, default="{}")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_eventlog_user_timestamp", "user_id", "timestamp"),
    )

    VALID_TYPES = {
        "nlp_message",
        "appointment_created",
        "habit_logged",
        "tool_called",
        "mood_detected",
        "error",
    }

    @classmethod
    def log(
        cls,
        db: Session,
        user_id: int,
        event_type: str,
        metadata: dict | None = None,
    ) -> "EventLog":
        entry = cls(
            user_id=user_id,
            event_type=event_type,
            metadata_=json.dumps(metadata or {}, ensure_ascii=False),
        )
        db.add(entry)
        db.commit()
        return entry

    @classmethod
    def get_weekly(cls, db: Session, user_id: int) -> list["EventLog"]:
        since = datetime.utcnow() - timedelta(days=7)
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.timestamp >= since)
            .all()
        )
