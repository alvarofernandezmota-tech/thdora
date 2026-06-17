"""Memoria persistente por usuario: perfil SQLite + resumen largo plazo."""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ThdoraMemory:
    """Gestor de memoria persistente por user_id."""

    def get_user_memory(self, user_id: int) -> dict[str, Any]:
        """Recupera memoria persistente del usuario."""
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
                return config.to_dict() if config else {"nombre": "Usuario", "preferencias": {}}
        except Exception as exc:
            logger.warning("No se pudo cargar perfil user_id=%s: %s", user_id, exc)
            return {"nombre": "Usuario", "preferencias": {}}

    def _load_long_term_summary(self, user_id: int) -> str:
        """Carga resumen largo plazo. TODO: implementar tabla summaries."""
        return ""


thdora_memory = ThdoraMemory()
