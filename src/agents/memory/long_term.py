"""
Memoria a largo plazo: resumen histórico por usuario.

Funciones para actualizar y recuperar la memoria histórica del usuario
(guardada en UserConfig.long_term_memory como texto comprimido).
"""
from __future__ import annotations
import logging
from datetime import datetime
from src.agents.config import agent_config

logger = logging.getLogger(__name__)


def update_long_term_memory(user_id: int, summary: str) -> None:
    """
    Actualiza la memoria a largo plazo del usuario.

    Antepone el nuevo resumen (con timestamp) al anterior.
    Recorta a agent_config.long_term_memory_max_length caracteres.

    Args:
        user_id: ID Telegram del usuario.
        summary: Nuevo resumen generado por el LLM.
    """
    try:
        from src.db.models import UserConfig
        from src.db.session import get_db
        with get_db() as db:
            config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            if config:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_entry = f"--- {ts} ---\n{summary}\n\n"
                current = getattr(config, "long_term_memory", "") or ""
                combined = new_entry + current
                max_len = agent_config.long_term_memory_max_length
                config.long_term_memory = combined[:max_len]
                db.commit()
                logger.info("long_term_memory actualizada para user_id=%s", user_id)
    except Exception as exc:
        logger.error("update_long_term_memory user_id=%s: %s", user_id, exc)
