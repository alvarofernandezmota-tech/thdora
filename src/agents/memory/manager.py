"""
Gestor único de memoria (ThdoraMemoryManager).

Punto central de acceso a toda la memoria del agente:
- Perfil de usuario (desde UserConfig en SQLite principal)
- Long-term memory (resumen generado por LLM, guardado en UserConfig)
- Checkpointer de LangGraph (SqliteSaver en data/thdora_memory.db)

Uso:
    from src.agents.memory.manager import memory_manager
    mem = memory_manager.get_memory(user_id)
"""
from __future__ import annotations
import logging
from typing import Any
from src.agents.config import agent_config

logger = logging.getLogger(__name__)


class ThdoraMemoryManager:
    """
    Gestor central de memoria por usuario.

    Attributes:
        checkpointer: SqliteSaver de LangGraph para persistencia de checkpoints.
    """

    def __init__(self) -> None:
        from langgraph.checkpoint.sqlite import SqliteSaver
        self.checkpointer = SqliteSaver.from_conn_string(agent_config.memory_db_path)

    def get_memory(self, user_id: int) -> dict[str, Any]:
        """
        Obtiene toda la memoria persistente del usuario.

        Combina perfil de UserConfig + long_term_memory para inyectar en el agente.

        Args:
            user_id: ID Telegram del usuario.

        Returns:
            Dict con user_name, long_term_memory y preferences.
        """
        try:
            from src.db.models import UserConfig
            from src.db.session import get_db
            with get_db() as db:
                config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
                if config:
                    return {
                        "user_id": user_id,
                        "user_name": getattr(config, "nombre", "Usuario") or "Usuario",
                        "long_term_memory": getattr(config, "long_term_memory", "") or "",
                        "preferences": getattr(config, "preferencias", {}) or {},
                    }
        except Exception as exc:
            logger.warning("get_memory user_id=%s: %s", user_id, exc)
        return {"user_id": user_id, "user_name": "Usuario", "long_term_memory": "", "preferences": {}}

    def update_long_term_memory(self, user_id: int, summary: str) -> None:
        """Delega en long_term.update_long_term_memory."""
        from .long_term import update_long_term_memory
        update_long_term_memory(user_id, summary)

    def cleanup(self, days_to_keep: int | None = None) -> None:
        """Delega en cleanup.cleanup_old_memory."""
        from .cleanup import cleanup_old_memory
        cleanup_old_memory(days_to_keep or agent_config.cleanup_days_to_keep)


memory_manager = ThdoraMemoryManager()
