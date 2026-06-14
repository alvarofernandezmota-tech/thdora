import uuid
import httpx
import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agents.orchestrator import AgentOrchestrator, get_orchestrator
from tools.registry import tool_registry

logger = logging.getLogger(__name__)

_THDORA_SYSTEM_PROMPT = """Eres THDORA, un asistente personal inteligente especializado en gestión \
de agenda y hábitos personales. Tienes acceso a las citas del usuario y puedes crear nuevas.

Reglas:
- Responde siempre en el mismo idioma que el usuario.
- Cuando el usuario pregunte por sus citas, usa get_appointments.
- Cuando el usuario quiera crear una cita, usa create_appointment con los datos extraídos.
- Si falta información para crear una cita (fecha, hora o título), pregunta antes de actuar.
- Sé conciso, amable y profesional.
"""

_THDORA_INTERNAL_API = "http://thdora-api:8000"


class AgentFactory:
    """Fábrica centralizada de orquestadores de agentes."""

    @classmethod
    def create(
        cls,
        agent_config: dict,
        tools_config: list[dict],
    ) -> AgentOrchestrator:
        """Crea un AgentOrchestrator a partir de config dicts (sin BD)."""
        return AgentOrchestrator(
            agent_id=uuid.UUID(str(agent_config["agent_id"])),
            system_prompt=agent_config["system_prompt"],
            tools_config=tools_config,
            model=agent_config.get("model", "llama-3.3-70b-versatile"),
            temperature=float(agent_config.get("temperature", 0.7)),
            max_tokens=int(agent_config.get("max_tokens", 4096)),
        )

    @classmethod
    async def create_from_db(
        cls,
        agent_id: uuid.UUID,
        db: AsyncSession,
        redis_client=None,
    ) -> AgentOrchestrator | None:
        orc = await get_orchestrator(agent_id, db, redis_client)
        if orc is None:
            return None
        enriched = []
        for tc in orc.tools_config:
            registered = tool_registry.get(tc["name"])
            if registered and registered.get("_impl"):
                tc = {**tc, "_impl": registered["_impl"]}
            enriched.append(tc)
        orc._lc_tools = AgentOrchestrator._build_lc_tools(enriched)
        return orc

    @classmethod
    async def create_thdora_agent(cls, db: AsyncSession) -> AgentOrchestrator:
        async def get_appointments(date: str | None = None) -> str:
            """Obtiene las citas del usuario. date: YYYY-MM-DD (opcional)."""
            params = {}
            if date:
                params["date"] = date
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    resp = await client.get(
                        f"{_THDORA_INTERNAL_API}/appointments", params=params
                    )
                    resp.raise_for_status()
                    return json.dumps(resp.json(), ensure_ascii=False)
                except httpx.HTTPError as exc:
                    logger.error("get_appointments error: %s", exc)
                    return json.dumps({"error": str(exc)})

        async def create_appointment(
            title: str,
            start_datetime: str,
            end_datetime: str,
            description: str = "",
        ) -> str:
            """Crea una nueva cita. Fechas en ISO 8601 (YYYY-MM-DDTHH:MM:SS)."""
            payload = {
                "title": title,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "description": description,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    resp = await client.post(
                        f"{_THDORA_INTERNAL_API}/appointments", json=payload
                    )
                    resp.raise_for_status()
                    return json.dumps(resp.json(), ensure_ascii=False)
                except httpx.HTTPError as exc:
                    logger.error("create_appointment error: %s", exc)
                    return json.dumps({"error": str(exc)})

        tools_config = [
            {
                "name": "get_appointments",
                "description": "Obtiene las citas del usuario para una fecha concreta.",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Fecha YYYY-MM-DD"}
                    },
                },
                "_impl": get_appointments,
            },
            {
                "name": "create_appointment",
                "description": "Crea una nueva cita en la agenda del usuario.",
                "json_schema": {
                    "type": "object",
                    "required": ["title", "start_datetime", "end_datetime"],
                    "properties": {
                        "title": {"type": "string"},
                        "start_datetime": {"type": "string"},
                        "end_datetime": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
                "_impl": create_appointment,
            },
        ]

        thdora_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        return AgentOrchestrator(
            agent_id=thdora_id,
            system_prompt=_THDORA_SYSTEM_PROMPT,
            tools_config=tools_config,
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=2048,
        )
