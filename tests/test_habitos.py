"""
Tests del handler de hábitos.
Verifica flujos: cmd_habitos, habito_start, recv_nombre, recv_value, conflict, editar.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import (
    TEST_DATE, TEST_USER_ID, TEST_HABIT, TEST_VALUE,
    make_update_message, make_update_callback, make_context,
)


@pytest.mark.asyncio
async def test_cmd_habitos_muestra_habitos(mock_api):
    """cmd_habitos llama a get_habits y responde con el listado."""
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import cmd_habitos
        update = make_update_message()
        ctx    = make_context()
        ctx.args = []
        await cmd_habitos(update, ctx)
        mock_api.get_habits.assert_awaited_once_with(TEST_DATE, TEST_USER_ID)


@pytest.mark.asyncio
async def test_habito_start_returns_nombre_state(mock_api):
    """habito_start limpia user_data y devuelve HABITO_NOMBRE."""
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import habito_start, HABITO_NOMBRE
        update = make_update_message()
        ctx    = make_context({"basura": True})
        result = await habito_start(update, ctx)
        assert result == HABITO_NOMBRE
        assert ctx.user_data.get("habito_user_id") == TEST_USER_ID
        assert "basura" not in ctx.user_data


@pytest.mark.asyncio
async def test_habito_recv_nombre_vacio_se_repite(mock_api):
    """Si el nombre está vacío, se mantiene en HABITO_NOMBRE."""
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import habito_recv_nombre_text, HABITO_NOMBRE
        update = make_update_message(text="   ")
        ctx    = make_context()
        result = await habito_recv_nombre_text(update, ctx)
        assert result == HABITO_NOMBRE


@pytest.mark.asyncio
async def test_habito_recv_nombre_valido_avanza(mock_api):
    """Nombre válido avanza al estado HABITO_VALUE."""
    mock_api.get_habit_config = AsyncMock(return_value=None)
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import habito_recv_nombre_text, HABITO_VALUE
        update = make_update_message(text=TEST_HABIT)
        ctx    = make_context({"habito_user_id": TEST_USER_ID, "habito_date": TEST_DATE})
        result = await habito_recv_nombre_text(update, ctx)
        assert result == HABITO_VALUE
        assert ctx.user_data["habito_nombre"] == TEST_HABIT


@pytest.mark.asyncio
async def test_save_habito_llama_log_habit(mock_api):
    """_save_habito llama a api.log_habit con los datos correctos."""
    mock_api.get_habits = AsyncMock(return_value={})  # sin hábito previo
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import _save_habito
        from telegram.ext import ConversationHandler
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "habito_nombre": TEST_HABIT,
            "habito_date":   TEST_DATE,
            "habito_user_id": TEST_USER_ID,
        })
        result = await _save_habito(msg, ctx, TEST_VALUE)
        mock_api.log_habit.assert_awaited_once_with(TEST_DATE, TEST_HABIT, TEST_VALUE, TEST_USER_ID)
        assert result == ConversationHandler.END


@pytest.mark.asyncio
async def test_conflict_detectado_cuando_existe_valor(mock_api):
    """Si ya existe valor y el input no empieza con '+', se pide confirmación."""
    mock_api.get_habits = AsyncMock(return_value={TEST_HABIT: "1L"})
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import _save_habito, HABITO_CONFLICT
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "habito_nombre": TEST_HABIT,
            "habito_date":   TEST_DATE,
            "habito_user_id": TEST_USER_ID,
        })
        result = await _save_habito(msg, ctx, "2L")
        assert result == HABITO_CONFLICT


@pytest.mark.asyncio
async def test_acumulacion_con_mas_no_genera_conflict(mock_api):
    """Si el valor empieza con '+', se acumula sin pedir confirmación."""
    mock_api.get_habits = AsyncMock(return_value={TEST_HABIT: "1L"})
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import _save_habito
        from telegram.ext import ConversationHandler
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "habito_nombre": TEST_HABIT,
            "habito_date":   TEST_DATE,
            "habito_user_id": TEST_USER_ID,
        })
        result = await _save_habito(msg, ctx, "+1L")
        assert result == ConversationHandler.END
        mock_api.log_habit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_habit_llama_api_delete(mock_api):
    """cb_hab_delete_confirm llama a api.delete_habit con user_id correcto."""
    with patch("src.bot.handlers.habitos.api", mock_api):
        from src.bot.handlers.habitos import cb_hab_delete_confirm
        update = make_update_callback(f"hdc_{TEST_DATE}_{TEST_HABIT}")
        ctx    = make_context()
        await cb_hab_delete_confirm(update, ctx)
        mock_api.delete_habit.assert_awaited_once_with(TEST_DATE, TEST_HABIT, TEST_USER_ID)
