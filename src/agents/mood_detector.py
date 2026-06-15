import json
import logging
from groq import AsyncGroq
from src.api.models.mood import MoodEntry
from src.api.deps import SessionLocal

logger = logging.getLogger(__name__)

_ANALYZE_PROMPT = """Eres un analizador de estado emocional. Analiza los siguientes mensajes de un usuario y devuelve UNICAMENTE un objeto JSON:
{"score": <entero 1-10 donde 1=muy negativo y 10=muy positivo>, "keywords": [<lista de 3-5 palabras clave emocionales en español>]}
No incluyas explicaciones ni texto adicional. Solo el JSON."""


class MoodDetector:
    def __init__(self, groq_api_key: str):
        self._groq = AsyncGroq(api_key=groq_api_key)

    async def analyze(self, messages: list[str], user_id: int) -> MoodEntry | None:
        if not messages:
            return None
        text_block = "\n".join(f"- {m}" for m in messages[-10:])
        try:
            response = await self._groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": _ANALYZE_PROMPT},
                    {"role": "user", "content": text_block},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            data = json.loads(raw)
            score = max(1, min(10, int(data.get("score", 5))))
            keywords = data.get("keywords", [])[:5]
            db = SessionLocal()
            try:
                entry = MoodEntry.save(db, user_id=user_id, score=score, keywords=keywords)
            finally:
                db.close()
            return entry
        except Exception as e:
            logger.warning("MoodDetector.analyze error: %s", e)
            return None

    async def should_mention(self, user_id: int) -> bool:
        from datetime import datetime, timedelta
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            low_days = 0
            for offset in range(3):
                day_start = now - timedelta(days=offset + 1)
                day_end = now - timedelta(days=offset)
                rows = (
                    db.query(MoodEntry)
                    .filter(
                        MoodEntry.user_id == user_id,
                        MoodEntry.timestamp >= day_start,
                        MoodEntry.timestamp < day_end,
                    )
                    .all()
                )
                if rows:
                    avg = sum(r.score for r in rows) / len(rows)
                    if avg < 4:
                        low_days += 1
            return low_days >= 3
        finally:
            db.close()

    async def get_thdora_response(self, trend: str) -> str:
        try:
            response = await self._groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres THDORA, un agente de bienestar emocional calido y empatico. "
                            "Genera un mensaje breve (2-3 frases) mencionando de forma natural "
                            "que has notado cierto patron en el estado emocional del usuario. "
                            "No seas alarmista. Ofrece escucha y apoyo."
                        ),
                    },
                    {"role": "user", "content": f"Patron detectado: {trend}"},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "He notado que estos dias no estas del todo bien. Aqui estoy si quieres contarme algo. 💙"
