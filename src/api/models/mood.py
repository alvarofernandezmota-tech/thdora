import json
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, Text, DateTime, Index
from sqlalchemy.orm import Session
from src.api.deps import Base


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    keywords = Column(Text, nullable=False, default="[]")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_mood_user_timestamp", "user_id", "timestamp"),
    )

    @property
    def keywords_list(self) -> list[str]:
        return json.loads(self.keywords)

    @classmethod
    def get_weekly_average(cls, db: Session, user_id: int) -> float | None:
        since = datetime.utcnow() - timedelta(days=7)
        rows = (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.timestamp >= since)
            .all()
        )
        if not rows:
            return None
        return round(sum(r.score for r in rows) / len(rows), 2)

    @classmethod
    def save(
        cls, db: Session, user_id: int, score: int, keywords: list[str]
    ) -> "MoodEntry":
        entry = cls(
            user_id=user_id,
            score=score,
            keywords=json.dumps(keywords, ensure_ascii=False),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
