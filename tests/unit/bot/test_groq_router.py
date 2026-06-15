"""Tests del system prompt del GroqRouter."""

from __future__ import annotations
import pytest
from src.bot.groq_router import build_system_prompt


def test_system_prompt_contains_username() -> None:
    prompt = build_system_prompt("Álvaro")
    assert "Álvaro" in prompt


def test_system_prompt_has_limits() -> None:
    prompt = build_system_prompt("Test")
    for kw in ["LÍMITES", "scope", "rechazas", "agenda", "hábitos"]:
        assert kw in prompt, f"Falta keyword: '{kw}'"


def test_system_prompt_has_examples() -> None:
    prompt = build_system_prompt("Test")
    assert "crear_cita" in prompt
    assert "registrar_habito" in prompt
    assert "consultar_semana" in prompt
    assert "fuera_de_scope" in prompt
    assert "poema" in prompt or "capital" in prompt


def test_build_prompt_no_username() -> None:
    prompt = build_system_prompt(None)
    assert "Usuario" in prompt
    assert "None" not in prompt
