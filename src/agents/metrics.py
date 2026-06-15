import logging
from src.api.models.event import EventLog
from src.api.models.mood import MoodEntry
from src.api.deps import SessionLocal

logger = logging.getLogger(__name__)


class MetricsCollector:
    async def log(self, user_id: int, event_type: str, metadata: dict | None = None) -> None:
        db = SessionLocal()
        try:
            EventLog.log(db, user_id=user_id, event_type=event_type, metadata=metadata)
        except Exception as e:
            logger.warning("MetricsCollector.log error: %s", e)
        finally:
            db.close()

    async def get_stats(self, user_id: int) -> dict:
        db = SessionLocal()
        try:
            events = EventLog.get_weekly(db, user_id=user_id)
            nlp_total = sum(1 for e in events if e.event_type == "nlp_message")
            nlp_ok = sum(
                1 for e in events
                if e.event_type == "nlp_message"
                and '"success": true' in e.metadata_
            )
            appts = sum(1 for e in events if e.event_type == "appointment_created")
            habits = sum(1 for e in events if e.event_type == "habit_logged")
            mood_avg = MoodEntry.get_weekly_average(db, user_id=user_id)
            success_rate = round(nlp_ok / nlp_total * 100) if nlp_total else 0
            return {
                "nlp_messages": nlp_total,
                "appointments_created": appts,
                "habits_logged": habits,
                "nlp_success_rate": success_rate,
                "mood_average": mood_avg,
            }
        except Exception as e:
            logger.warning("MetricsCollector.get_stats error: %s", e)
            return {}
        finally:
            db.close()
