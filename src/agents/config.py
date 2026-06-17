"""
Configuración centralizada del Agente THDORA.

Todas las configuraciones de LLM, memoria y comportamiento del agente.
Usa Pydantic para validación y soporte de variables de entorno con prefijo AGENT_.
"""
from __future__ import annotations
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """
    Configuración del sistema de agentes.

    Attributes:
        default_model: Modelo Groq a utilizar.
        temperature: Creatividad del modelo (0.0 = determinista).
        max_tokens: Límite de tokens por respuesta.
        memory_db_path: Ruta de la base de datos de memoria persistente (SqliteSaver).
        long_term_memory_max_length: Límite de caracteres para long_term_memory.
        cleanup_days_to_keep: Días de historial de checkpoints a conservar.
    """

    default_model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_tokens: int = 1024
    memory_db_path: str = "data/thdora_memory.db"
    long_term_memory_max_length: int = 4000
    cleanup_days_to_keep: int = 90

    model_config = {"env_prefix": "AGENT_", "env_file": ".env", "extra": "ignore"}


agent_config = AgentConfig()
