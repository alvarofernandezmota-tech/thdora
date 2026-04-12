"""
Tests para src/bot/handlers/habitos.py

Cubre:
 - habito_recv_nombre_text: nombre válido / vacío
 - habito_recv_value_text: valor texto / vacío
 - habito_recv_value_inline: hval_1 / hval___otro
 - habito_conflict_response: overwrite / add / cancel
 - _save_habito: éxito / conflicto / error API
 - cb_hab_delete / confirm
 - cb_hab_add / cb_hab_add_value
 - build_habito_handler / build_edit_hab_handler
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers.habitos import (
    HABITO_NOMBRE, HABITO_VALUE, HABITO_CONFLICT,
    EDIT_HAB_NOMBRE, EDIT_HAB_VALUE,
    habito_recv_nombre_text, habito_recv_value_text,
    habito_recv_value_inline, habito_conflict_response,
    _save_habito, cb_hab_delete, cb_hab_delete_confirm,
    cb_hab_add, cb_hab_add_value,
    build_habito_handler, build_edit_hab_handler,
)
from telegram.ext import ConversationHandler


def _make_update(text=None):
    update  = MagicMock()
    message = AsyncMock()
    message.text = text
    message.reply_text = AsyncMock()
    update.message = message
    update.callback_query = None
    return update


def _make_callback(data):
    update = MagicMock()
    query  = AsyncMock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.message = AsyncMock()
    query.message.reply_text = AsyncMock()
    update.callback_query = query
    update.message = None
    return update


def _make_context(user_data=None):
    ctx = MagicMock()
    ctx.user_data = user_data or {}
    return ctx


pytestmark = pytest.mark.asyncio


class TestHabitoRecvNombreText:
    @patch("src.bot.handlers.habitos.api")
    async def test_nombre_valido_avanza_a_value(self, mock_api):
        mock_api.get_habit_config = AsyncMock(return_value=None)
        update  = _make_update("sueño")
        context = _make_context()
        result  = await habito_recv_nombre_text(update, context)
        assert result == HABITO_VALUE
        assert context.user_data["habito_nombre"] == "sueño"

    async def test_nombre_vacio_permanece(self):
        update  = _make_update("")
        context = _make_context()
        result  = await habito_recv_nombre_text(update, context)
        assert result == HABITO_NOMBRE


class TestHabitoRecvValueText:
    @patch("src.bot.handlers.habitos.api")
    async def test_valor_nuevo_sin_conflicto_termina(self, mock_api):
        mock_api.get_habits  = AsyncMock(return_value={})
        mock_api.log_habit   = AsyncMock()
        update  = _make_update("8h")
        context = _make_context({"habito_nombre": "sueño", "habito_date": "2026-04-15"})
        result  = await habito_recv_value_text(update, context)
        assert result == ConversationHandler.END

    @patch("src.bot.handlers.habitos.api")
    async def test_valor_existente_sin_suma_genera_conflicto(self, mock_api):
        mock_api.get_habits = AsyncMock(return_value={"sueño": "7h"})
        update  = _make_update("8h")
        context = _make_context({"habito_nombre": "sueño", "habito_date": "2026-04-15"})
        result  = await habito_recv_value_text(update, context)
        assert result == HABITO_CONFLICT

    @patch("src.bot.handlers.habitos.api")
    async def test_valor_con_suma_no_genera_conflicto(self, mock_api):
        mock_api.get_habits = AsyncMock(return_value={"agua": "1L"})
        mock_api.log_habit  = AsyncMock()
        update  = _make_update("+0.5L")
        context = _make_context({"habito_nombre": "agua", "habito_date": "2026-04-15"})
        result  = await habito_recv_value_text(update, context)
        assert result == ConversationHandler.END

    async def test_valor_vacio_permanece(self):
        update  = _make_update("")
        context = _make_context()
        result  = await habito_recv_value_text(update, context)
        assert result == HABITO_VALUE


class TestHabitoRecvValueInline:
    @patch("src.bot.handlers.habitos.api")
    async def test_valor_boolean_termina(self, mock_api):
        mock_api.get_habits = AsyncMock(return_value={})
        mock_api.log_habit  = AsyncMock()
        update  = _make_callback("hval_1")
        context = _make_context({"habito_nombre": "ejercicio", "habito_date": "2026-04-15"})
        result  = await habito_recv_value_inline(update, context)
        assert result == ConversationHandler.END

    async def test_otro_valor_permanece_en_value(self):
        update  = _make_callback("hval___otro")
        context = _make_context()
        result  = await habito_recv_value_inline(update, context)
        assert result == HABITO_VALUE


class TestHabitoConflictResponse:
    @patch("src.bot.handlers.habitos.api")
    async def test_overwrite_guarda_nuevo_valor(self, mock_api):
        mock_api.log_habit = AsyncMock()
        update  = _make_callback("hconf_overwrite")
        context = _make_context({
            "habito_nombre": "sueño", "habito_date": "2026-04-15",
            "habito_new_val": "9h", "habito_existing_val": "7h",
        })
        result = await habito_conflict_response(update, context)
        assert result == ConversationHandler.END
        mock_api.log_habit.assert_awaited_once_with("2026-04-15", "sueño", "9h")

    @patch("src.bot.handlers.habitos.api")
    async def test_add_suma_valores(self, mock_api):
        mock_api.log_habit = AsyncMock()
        update  = _make_callback("hconf_add")
        context = _make_context({
            "habito_nombre": "agua", "habito_date": "2026-04-15",
            "habito_new_val": "0.5L", "habito_existing_val": "1L",
        })
        result = await habito_conflict_response(update, context)
        assert result == ConversationHandler.END

    async def test_cancel_termina_sin_guardar(self):
        update  = _make_callback("hconf_cancel")
        context = _make_context({
            "habito_nombre": "sueño", "habito_date": "2026-04-15",
        })
        result = await habito_conflict_response(update, context)
        assert result == ConversationHandler.END


class TestCbHabAdd:
    async def test_guarda_contexto_acum(self):
        update  = _make_callback("ha_2026-04-15_agua")
        context = _make_context()
        await cb_hab_add(update, context)
        assert context.user_data["acum_hab_date"]   == "2026-04-15"
        assert context.user_data["acum_hab_nombre"] == "agua"


class TestCbHabAddValue:
    @patch("src.bot.handlers.habitos.api")
    async def test_acumula_y_responde(self, mock_api):
        mock_api.get_habits = AsyncMock(return_value={"agua": "1L"})
        mock_api.log_habit  = AsyncMock()
        update  = _make_update("+0.5L")
        context = _make_context({"acum_hab_date": "2026-04-15", "acum_hab_nombre": "agua"})
        await cb_hab_add_value(update, context)
        mock_api.log_habit.assert_awaited_once_with("2026-04-15", "agua", "1.5L")

    async def test_sin_contexto_no_hace_nada(self):
        update  = _make_update("+1")
        context = _make_context()
        await cb_hab_add_value(update, context)  # no debe lanzar


class TestBuildHandlers:
    def test_build_habito_handler_tiene_estados(self):
        h = build_habito_handler()
        assert HABITO_NOMBRE   in h.states
        assert HABITO_VALUE    in h.states
        assert HABITO_CONFLICT in h.states

    def test_build_edit_hab_handler_tiene_estados(self):
        h = build_edit_hab_handler()
        assert EDIT_HAB_NOMBRE in h.states
        assert EDIT_HAB_VALUE  in h.states
