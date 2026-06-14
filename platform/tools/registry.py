"""Tool Registry — carga y gestiona tools disponibles para los agentes."""
from typing import Callable, Dict

_TOOL_REGISTRY: Dict[str, Callable] = {}


def register(name: str):
    """Decorador para registrar una función como tool disponible."""
    def decorator(fn: Callable) -> Callable:
        _TOOL_REGISTRY[name] = fn
        return fn
    return decorator


def get_tool(name: str) -> Callable | None:
    return _TOOL_REGISTRY.get(name)


def list_registered_tools() -> list[str]:
    return list(_TOOL_REGISTRY.keys())
