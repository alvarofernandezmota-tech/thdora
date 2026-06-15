"""Tests del módulo de contexto dinámico para el LLM."""

from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.bot.groq_context import build_context


def _make_api_client(citas=None, habitos=None):
    client = MagicMock()
    if isinstance(citas, Exception):
        client.get_appointments = AsyncMock(side_effect=citas)
    else:
        client.get_appointments = AsyncMock(return_value=citas or [])
    if isinstance(habitos, Exception):
        client.get_habits = AsyncMock(side_effect=habitos)
    else:
        client.get_habits = AsyncMock(return_value=habitos or [])
    return client


@pytest.mark.asyncio
async def test_build_context_parallel_calls() -> None:
    client = _make_api_client(
        citas=[{"hora": "10:30", "nombre": "Dentista"}],
        habitos=[{"nombre": "Agua", "completado_hoy": True}],
    )
    await build_context(user_id=1, api_client=client)
    client.get_appointments.assert_awaited_once()
    client.get_habits.assert_awaited_once()


@pytest.mark.asyncio
async def test_build_context_format() -> None:
    client = _make_api_client(
        citas=[{"hora": "10:30", "nombre": "Dentista"}, {"hora": "16:00", "nombre": "Gym"}],
        habitos=[{"nombre": "Agua", "completado_hoy": True}, {"nombre": "Ejercicio", "completado_hoy": False}],
    )
    result = await build_context(user_id=1, api_client=client)
    assert "CITAS HOY:" in result
    assert "HÁBITOS:" in result
    assert "Dentista" in result
    assert "Gym" in result
    assert "✅" in result
    assert "⬜" in result
    assert "Son las" in result


@pytest.mark.asyncio
async def test_build_context_api_failure() -> None:
    client = _make_api_client(citas=RuntimeError("API caída"), habitos=RuntimeError("API caída"))
    result = await build_context(user_id=1, api_client=client)
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_context_injected_in_prompt() -> None:
    client = _make_api_client(
        citas=[{"hora": "09:00", "nombre": "Reunión"}],
        habitos=[{"nombre": "Meditación", "completado_hoy": False}],
    )
    context_str = await build_context(user_id=1, api_client=client)
    assert "Reunión" in context_str
    assert "Meditación" in context_str
