"""
THDORA Agents Package
=====================

Módulo principal que expone el sistema de agentes inteligentes de THDORA.
Contiene todo el "cerebro": LangGraph, memoria persistente, tools y prompts.

Uso:
    from src.agents import build_thdora_graph, memory_manager
"""
from .core.graph import build_thdora_graph
from .memory.manager import memory_manager
from .config import agent_config

__version__ = "0.21.0"
__all__ = ["build_thdora_graph", "memory_manager", "agent_config"]
