"""Tests unitarios del handler NLP con patrón provisional + edición."""

from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock
import httpx
import pytest
from telegram.error import NetworkError
from src.bot.handlers.nlp import nlp_handler


def _make_update(text: str = "Crea una cita mañana") -> MagicMock:
    update = MagicMock()
    update.message = AsyncMock()
    update.message.text = text
    update.message.reply_text = AsyncMock(return_value=MagicMock(message_id=42))
    update.effective_user = MagicMock(id=999)
    update.effective_chat = MagicMock(id=999)
    return update


def _make_context(groq_response: str = "Cita creada ✅") -> MagicMock:
    context = MagicMock()
    context.bot = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    mock_router = AsyncMock()
    mock_router.process = AsyncMock(return_value=groq_response)
    context.bot_data = {"groq_router": mock_router}
    return context


@pytest.mark.asyncio
async def test_nlp_sends_processing_message() -> None:
    update = _make_update()
    context = _make_context()
    await nlp_handler(update, context)
    update.message.reply_text.assert_awaited_once()
    call_args = update.message.reply_text.call_args[0]
    assert "⏳" in call_args[0] or "Procesando" in call_args[0]


@pytest.mark.asyncio
async def test_nlp_edits_with_response() -> None:
    update = _make_update()
    context = _make_context(groq_response="Cita creada para mañana ✅")
    await nlp_handler(update, context)
    context.bot.edit_message_text.assert_awaited_once()
    kwargs = context.bot.edit_message_text.call_args.kwargs
    assert "Cita creada para mañana ✅" in kwargs.get("text", "")
    assert kwargs.get("message_id") == 42


@pytest.mark.asyncio
async def test_nlp_timeout_shows_error() -> None:
    update = _make_update()
    context = _make_context()
    context.bot_data["groq_router"].process.side_effect = httpx.TimeoutException("read timeout")
    await nlp_handler(update, context)
    context.bot.edit_message_text.assert_awaited_once()
    text = context.bot.edit_message_text.call_args.kwargs.get("text", "")
    assert "⌛" in text or "tiempo" in text.lower()


@pytest.mark.asyncio
async def test_nlp_network_error_handled() -> None:
    update = _make_update()
    context = _make_context()
    context.bot_data["groq_router"].process.side_effect = NetworkError("red caída")
    await nlp_handler(update, context)
    context.bot.edit_message_text.assert_awaited_once()
    text = context.bot.edit_message_text.call_args.kwargs.get("text", "")
    assert "📡" in text or "red" in text.lower() or "conexión" in text.lower()


@pytest.mark.asyncio
async def test_nlp_connect_error_handled() -> None:
    update = _make_update()
    context = _make_context()
    context.bot_data["groq_router"].process.side_effect = httpx.ConnectError("connection refused")
    await nlp_handler(update, context)
    context.bot.edit_message_text.assert_awaited_once()
    text = context.bot.edit_message_text.call_args.kwargs.get("text", "")
    assert "🔌" in text or "conectar" in text.lower()
