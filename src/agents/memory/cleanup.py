"""
Limpieza automática de memoria antigua.

Funciones para:
- Recortar long_term_memory de todos los usuarios al límite configurado.
- Eliminar checkpoints LangGraph más antiguos que N días.

Llamadas desde scheduler_tasks.py (lunes 2:00 AM).
"""
from __future__ import annotations
import logging
import sqlite3
from datetime import datetime, timedelta
from src.agents.config import agent_config

logger = logging.getLogger(__name__)


def cleanup_old_memory(days_to_keep: int = 90) -> None:
    """
    Limpieza completa de memoria antigua.

    1. Recorta long_term_memory de todos los usuarios.
    2. Elimina checkpoints LangGraph más viejos que days_to_keep.

    Args:
        days_to_keep: Número de días de historial a conservar.
    """
    _trim_all_long_term_memory()
    _cleanup_langgraph_checkpoints(days_to_keep)
    logger.info("🧹 Limpieza de memoria completada (conservando %s días)", days_to_keep)


def _trim_all_long_term_memory() -> None:
    """Recorta long_term_memory de todos los usuarios al límite configurado."""
    max_len = agent_config.long_term_memory_max_length
    try:
        from src.db.models import UserConfig
        from src.db.session import get_db
        with get_db() as db:
            updated = 0
            for user in db.query(UserConfig).all():
                mem = getattr(user, "long_term_memory", "") or ""
                if len(mem) > max_len:
                    # Conserva entradas más recientes (inicio del string)
                    user.long_term_memory = mem[:max_len]
                    updated += 1
            if updated:
                db.commit()
                logger.info("_trim: %s usuarios recortados", updated)
    except Exception as exc:
        logger.warning("_trim_all_long_term_memory error: %s", exc)


def _cleanup_langgraph_checkpoints(days_to_keep: int) -> None:
    """Elimina checkpoints LangGraph más viejos que days_to_keep días."""
    try:
        cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        conn = sqlite3.connect(agent_config.memory_db_path)
        cur = conn.cursor()
        for table in ("checkpoints", "checkpoint_blobs", "checkpoint_writes"):
            try:
                cur.execute(f"DELETE FROM {table} WHERE created_at < ?", (cutoff,))  # noqa: S608
            except sqlite3.OperationalError:
                pass  # tabla no existe aún — ignorar
        conn.commit()
        conn.close()
        logger.info("_cleanup_langgraph_checkpoints: cutoff=%s", cutoff)
    except Exception as exc:
        logger.warning("_cleanup_langgraph_checkpoints error: %s", exc)
