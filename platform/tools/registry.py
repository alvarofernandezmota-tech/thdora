import uuid
import logging
from typing import Any

import jsonschema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agents.models import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registro central de tools con caché in-memory e invalidación."""

    def __init__(self) -> None:
        self._tools: dict[str, dict] = {}
        self._agent_cache: dict[str, list[dict]] = {}

    @staticmethod
    def _validate_schema(json_schema: dict) -> None:
        """Valida que json_schema sea un objeto JSON Schema Draft-7 válido."""
        try:
            jsonschema.Draft7Validator.check_schema(json_schema)
        except jsonschema.SchemaError as exc:
            raise ValueError(f"Invalid JSON Schema Draft-7: {exc.message}") from exc

    async def load_from_db(self, db: AsyncSession) -> None:
        """Carga todas las tools activas desde la base de datos."""
        result = await db.execute(select(Tool))
        tools = result.scalars().all()
        for tool in tools:
            self._tools[tool.name] = {
                "name": tool.name,
                "description": tool.description,
                "json_schema": tool.json_schema,
                "implementation_ref": tool.implementation_ref,
                "category": tool.category,
                "_impl": None,
            }
        self._agent_cache.clear()
        logger.info("ToolRegistry: cargadas %d tools desde BD", len(tools))

    def register(
        self,
        name: str,
        description: str,
        json_schema: dict,
        impl=None,
        category: str | None = None,
    ) -> None:
        """Registra una tool en runtime. Lanza ValueError si el schema es inválido."""
        self._validate_schema(json_schema)
        self._tools[name] = {
            "name": name,
            "description": description,
            "json_schema": json_schema,
            "category": category,
            "_impl": impl,
        }
        self._agent_cache.clear()
        logger.debug("ToolRegistry: registrada tool '%s'", name)

    def unregister(self, name: str) -> None:
        """Elimina una tool del registro e invalida la caché."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        del self._tools[name]
        self._agent_cache.clear()
        logger.debug("ToolRegistry: eliminada tool '%s'", name)

    def get(self, name: str) -> dict | None:
        return self._tools.get(name)

    def all(self) -> list[dict]:
        return list(self._tools.values())

    def get_tools_for_agent(self, agent_id: uuid.UUID, active_tools: list[str]) -> list[dict]:
        cache_key = f"{agent_id}:{','.join(sorted(active_tools))}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]
        result = [self._tools[n] for n in active_tools if n in self._tools]
        self._agent_cache[cache_key] = result
        return result


# Instancia global
tool_registry = ToolRegistry()
