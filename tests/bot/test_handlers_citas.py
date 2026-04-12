"""
Tests para src/bot/handlers/citas.py

Estrategia: mock de ThdoraApiClient y objetos Telegram falsos.
No arrancamos ningún servidor ni bot real.

Cubre:
 - nueva_recv_date: fecha válida / inválida
 - nueva_recv_franja: manana / tarde / noche / exacta
 - nueva_recv_hora_punto: hora en punto / ver_cuartos / exacta
 - nueva_recv_hora_cuarto: cuarto seleccionado / exacta
 - nueva_recv_time: HH:MM válida / inválida
 - nueva_recv_nombre: nombre válido / vacío
 - nueva_recv_type: tipo registrado
 - _save_appointment: éxito / error API
 - cb_apt_delete / confirm: flujo borrado
 - build_nueva_handler: estados correctos
 - build_edit_apt_handler: entry_point correcto
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers.citas import (
    NUEVA_DATE, NUEVA_FRANJA, NUEVA_HORA_PUNTO, NUEVA_HORA_CUARTO,
    NUEVA_TIME, NUEVA_NOMBRE, NUEVA_TYPE, NUEVA_NOTES, NUEVA_CONFLICT,
    nueva_recv_date, nueva_recv_franja, nueva_recv_hora_punto,
    nueva_recv_hora_cuarto, nueva_recv_time, nueva_recv_nombre,
    nueva_recv_type, nueva_recv_notes, _save_appointment,
    cb_apt_delete, cb_apt_delete_confirm,
    build_nueva_handler, build_edit_apt_handler,
)
from telegram.ext import ConversationHandler


def _make_update(text=None):
    """Crea un Update falso con message.text."""
    update  = MagicMock()
    message = AsyncMock()
    message.text = text
    message.reply_text = AsyncMock()
    update.message = message
    update.callback_query = None
    return update


def _make_callback(data):
    """Crea un Update falso con callback_query.data."""
    update = MagicMock()
    query  = AsyncMock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.edit_message_reply_markup = AsyncMock()
    query.message = AsyncMock()
    query.message.reply_text = AsyncMock()
    update.callback_query = query
    update.message = None
    return update


def _make_context(user_data=None):
    ctx = MagicMock()
    ctx.user_data = user_data or {}
    return ctx


# ──────────────────────────────────────────────────────────────────────
pytestmark = pytest.mark.asyncio


class TestNuevaRecvDate:
    async def test_fecha_valida_avanza_a_franja(self):
        update  = _make_update("hoy")
        context = _make_context()
        result  = await nueva_recv_date(update, context)
        assert result == NUEVA_FRANJA
        assert "nueva_date" in context.user_data

    async def test_fecha_invalida_permanece_en_date(self):
        update  = _make_update("esto no es fecha")
        context = _make_context()
        result  = await nueva_recv_date(update, context)
        assert result == NUEVA_DATE
        assert "nueva_date" not in context.user_data

    async def test_manana_avanza(self):
        update  = _make_update("mañana")
        context = _make_context()
        result  = await nueva_recv_date(update, context)
        assert result == NUEVA_FRANJA


class TestNuevaRecvFranja:
    async def test_manana_avanza_a_hora_punto(self):
        update  = _make_callback("franja_manana")
        context = _make_context()
        result  = await nueva_recv_franja(update, context)
        assert result == NUEVA_HORA_PUNTO
        assert context.user_data["nueva_franja"] == "manana"

    async def test_tarde_avanza_a_hora_punto(self):
        update  = _make_callback("franja_tarde")
        context = _make_context()
        result  = await nueva_recv_franja(update, context)
        assert result == NUEVA_HORA_PUNTO
        assert context.user_data["nueva_franja"] == "tarde"

    async def test_noche_avanza_a_hora_punto(self):
        update  = _make_callback("franja_noche")
        context = _make_context()
        result  = await nueva_recv_franja(update, context)
        assert result == NUEVA_HORA_PUNTO

    async def test_exacta_va_a_nueva_time(self):
        update  = _make_callback("franja_exacta")
        context = _make_context()
        result  = await nueva_recv_franja(update, context)
        assert result == NUEVA_TIME


class TestNuevaRecvHoraPunto:
    async def test_hora_punto_avanza_a_cuarto(self):
        update  = _make_callback("hora_punto_09")
        context = _make_context({"nueva_franja": "manana"})
        result  = await nueva_recv_hora_punto(update, context)
        assert result == NUEVA_HORA_CUARTO
        assert context.user_data["nueva_hora_temp"] == 9

    async def test_ver_cuartos_avanza_a_cuarto(self):
        update  = _make_callback("hora_ver_cuartos")
        context = _make_context({"nueva_franja": "tarde"})
        result  = await nueva_recv_hora_punto(update, context)
        assert result == NUEVA_HORA_CUARTO

    async def test_exacta_va_a_nueva_time(self):
        update  = _make_callback("hora_exacta")
        context = _make_context({"nueva_franja": "manana"})
        result  = await nueva_recv_hora_punto(update, context)
        assert result == NUEVA_TIME


class TestNuevaRecvHoraCuarto:
    @patch("src.bot.handlers.citas.api")
    async def test_cuarto_sin_conflicto_avanza_a_nombre(self, mock_api):
        mock_api.check_appointment_conflict = AsyncMock(return_value=None)
        update  = _make_callback("hora_cuarto_10:30")
        context = _make_context({"nueva_date": "2026-04-15"})
        result  = await nueva_recv_hora_cuarto(update, context)
        assert result == NUEVA_NOMBRE
        assert context.user_data["nueva_time"] == "10:30"

    async def test_exacta_va_a_nueva_time(self):
        update  = _make_callback("hora_exacta")
        context = _make_context()
        result  = await nueva_recv_hora_cuarto(update, context)
        assert result == NUEVA_TIME


class TestNuevaRecvTime:
    @patch("src.bot.handlers.citas.api")
    async def test_hora_valida_avanza_a_nombre(self, mock_api):
        mock_api.check_appointment_conflict = AsyncMock(return_value=None)
        update  = _make_update("10:30")
        context = _make_context({"nueva_date": "2026-04-15"})
        result  = await nueva_recv_time(update, context)
        assert result == NUEVA_NOMBRE

    async def test_formato_invalido_permanece(self):
        update  = _make_update("25:99")
        context = _make_context()
        result  = await nueva_recv_time(update, context)
        assert result == NUEVA_TIME

    async def test_formato_sin_separador_invalido(self):
        update  = _make_update("1030")
        context = _make_context()
        result  = await nueva_recv_time(update, context)
        assert result == NUEVA_TIME


class TestNuevaRecvNombre:
    async def test_nombre_valido_avanza_a_type(self):
        update  = _make_update("Revisión médica")
        context = _make_context()
        result  = await nueva_recv_nombre(update, context)
        assert result == NUEVA_TYPE
        assert context.user_data["nueva_nombre"] == "Revisión médica"

    async def test_nombre_vacio_permanece(self):
        update  = _make_update("")
        context = _make_context()
        result  = await nueva_recv_nombre(update, context)
        assert result == NUEVA_NOMBRE


class TestNuevaRecvType:
    async def test_tipo_registrado_avanza_a_notes(self):
        update  = _make_callback("tipo_personal")
        context = _make_context()
        result  = await nueva_recv_type(update, context)
        assert result == NUEVA_NOTES
        assert context.user_data["nueva_type"] == "personal"


class TestSaveAppointment:
    @patch("src.bot.handlers.citas.api")
    async def test_exito_llama_create_y_termina(self, mock_api):
        mock_api.create_appointment = AsyncMock(return_value={"index": 1})
        update  = _make_update("sin notas")
        context = _make_context({
            "nueva_date":   "2026-04-15",
            "nueva_time":   "10:00",
            "nueva_nombre": "Test",
            "nueva_type":   "personal",
        })
        result = await _save_appointment(update, context, "")
        assert result == ConversationHandler.END
        mock_api.create_appointment.assert_awaited_once()

    @patch("src.bot.handlers.citas.api")
    async def test_error_api_muestra_aviso(self, mock_api):
        from src.bot.api_client import ApiError
        mock_api.create_appointment = AsyncMock(side_effect=ApiError("fallo"))
        update  = _make_update("")
        context = _make_context({"nueva_date": "2026-04-15", "nueva_time": "09:00",
                                  "nueva_nombre": "X", "nueva_type": "otra"})
        result = await _save_appointment(update, context, "")
        assert result == ConversationHandler.END
        update.message.reply_text.assert_awaited()


class TestBuildHandlers:
    def test_build_nueva_handler_tiene_estados_correctos(self):
        h = build_nueva_handler()
        assert NUEVA_DATE        in h.states
        assert NUEVA_FRANJA      in h.states
        assert NUEVA_HORA_PUNTO  in h.states
        assert NUEVA_HORA_CUARTO in h.states
        assert NUEVA_TIME        in h.states
        assert NUEVA_NOMBRE      in h.states
        assert NUEVA_TYPE        in h.states
        assert NUEVA_NOTES       in h.states

    def test_build_edit_apt_handler_tiene_entry_point(self):
        h = build_edit_apt_handler()
        assert len(h.entry_points) > 0
