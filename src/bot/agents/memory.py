"""Memoria persistente por usuario: perfil SQLite + resumen largo plazo + limpieza."""
from __future__ import annotations
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class ThdoraMemory:
    """Gestor de memoria persistente por user_id."""

    def get_user_memory(self, user_id: int) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "profile": self._load_user_profile(user_id),
            "summary": self._load_long_term_summary(user_id),
        }

    def _load_user_profile(self, user_id: int) -> dict:
        try:
            from src.db.models import UserConfig
            from src.db.session import get_db
            with get_db() as db:
                config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
                if config:
                    return {
                        "nombre": getattr(config, "nombre", "Usuario") or "Usuario",
                        "preferencias": getattr(config, "preferencias", {}) or {},
                        "zona_horaria": getattr(config, "zona_horaria", "Europe/Madrid"),
                    }
        except Exception as exc:
            logger.warning("No se pudo cargar perfil user_id=%s: %s", user_id, exc)
        return {"nombre": "Usuario", "preferencias": {}, "zona_horaria": "Europe/Madrid"}

    def _load_long_term_summary(self, user_id: int) -> str:
        try:
            from src.db.models import UserConfig
            from src.db.session import get_db
            with get_db() as db:
                config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
                return getattr(config, "long_term_memory", "") or ""
        except Exception as exc:
            logger.warning("No se pudo cargar long_term_memory user_id=%s: %s", user_id, exc)
        return ""

    def save_long_term_summary(self, user_id: int, summary: str) -> None:
        try:
            from src.db.models import UserConfig
            from src.db.session import get_db
            with get_db() as db:
                config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
                if config:
                    config.long_term_memory = summary
                    db.commit()
        except Exception as exc:
            logger.error("save_long_term_summary user_id=%s: %s", user_id, exc)

    def cleanup_old_memory(self, days_to_keep: int = 90) -> None:
        """Limpia memoria antigua: recorta long_term_memory + borra checkpoints viejos."""
        self._trim_long_term_memory(max_length=3000)
        self._cleanup_langgraph_checkpoints(days_to_keep)
        logger.info("🧹 Limpieza completada (manteniendo %s días)", days_to_keep)

    def _trim_long_term_memory(self, max_length: int = 3000) -> None:
        try:
            from src.db.models import UserConfig
            from src.db.session import get_db
            with get_db() as db:
                for user in db.query(UserConfig).all():
                    mem = getattr(user, "long_term_memory", "") or ""
                    if len(mem) > max_length:
                        parts = mem.split("\n\n--- Actualizado")
                        if len(parts) > 5:
                            user.long_term_memory = "--- Actualizado".join(parts[-5:])
                        else:
                            user.long_term_memory = mem[-max_length:]
                db.commit()
        except Exception as exc:
            logger.warning("_trim_long_term_memory error: %s", exc)

    def _cleanup_langgraph_checkpoints(self, days_to_keep: int = 90) -> None:
        try:
            cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            conn = sqlite3.connect("data/thdora_memory.db")
            cur = conn.cursor()
            for table in ("checkpoints", "checkpoint_blobs"):
                try:
                    cur.execute(f"DELETE FROM {table} WHERE created_at < ?", (cutoff,))
                except sqlite3.OperationalError:
                    pass  # tabla no existe aún
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.warning("_cleanup_langgraph_checkpoints error: %s", exc)


thdora_memory = ThdoraMemory()
