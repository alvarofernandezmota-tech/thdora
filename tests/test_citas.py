"""
Tests del handler de citas.
Verifica create, delete, conflict detection, _find_overlap.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import (
    TEST_DATE, TEST_USER_ID, TEST_APT_NAME, TEST_APT_TIME,
    make_update_callback, make_context,
)


@pytest.mark.asyncio
async def test_find_overlap_detects_conflict(mock_api):
    """_find_overlap devuelve la cita conflictiva si ya existe en ese horario."""
    mock_api.get_appointments = AsyncMock(return_value=[
        {"name": "Existente", "time": "10:00"}
    ])
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import _find_overlap
        conflict = await _find_overlap(TEST_DATE, "10:00", TEST_USER_ID)
        assert conflict is not None
        assert conflict["name"] == "Existente"


@pytest.mark.asyncio
async def test_find_overlap_no_conflict(mock_api):
    """_find_overlap devuelve None si el horario está libre."""
    mock_api.get_appointments = AsyncMock(return_value=[
        {"name": "Existente", "time": "09:00"}
    ])
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import _find_overlap
        conflict = await _find_overlap(TEST_DATE, "10:00", TEST_USER_ID)
        assert conflict is None


@pytest.mark.asyncio
async def test_delete_apt_confirm_llama_api(mock_api):
    """cb_apt_delete_confirm llama a api.delete_appointment con user_id correcto."""
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import cb_apt_delete_confirm
        update = make_update_callback(f"aptdc_{TEST_DATE}_0")
        ctx    = make_context()
        await cb_apt_delete_confirm(update, ctx)
        mock_api.delete_appointment.assert_awaited_once_with(TEST_DATE, 0, TEST_USER_ID)


@pytest.mark.asyncio
async def test_save_appointment_llama_create(mock_api):
    """_save_appointment llama a api.create_appointment con data:dict + user_id."""
    mock_api.get_appointments = AsyncMock(return_value=[])  # sin conflicto
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import _save_appointment
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "nueva_date":    TEST_DATE,
            "nueva_nombre":  TEST_APT_NAME,
            "nueva_hora":    TEST_APT_TIME,
            "nueva_tipo":    "trabajo",
            "nueva_notas":   "",
            "nueva_user_id": TEST_USER_ID,
        })
        from telegram.ext import ConversationHandler
        result = await _save_appointment(msg, ctx)
        mock_api.create_appointment.assert_awaited_once()
        call_args = mock_api.create_appointment.call_args
        # Verificar que se pasó data como dict y user_id
        assert call_args[0][0] == TEST_DATE
        assert isinstance(call_args[0][1], dict)
        assert call_args[0][2] == TEST_USER_ID
        assert result == ConversationHandler.END


@pytest.mark.asyncio
async def test_save_appointment_detecta_conflict(mock_api):
    """_save_appointment muestra pantalla de conflicto si el horario está ocupado."""
    mock_api.get_appointments = AsyncMock(return_value=[
        {"name": "Otra cita", "time": TEST_APT_TIME}
    ])
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import _save_appointment, NUEVA_CONFLICT
        msg = AsyncMock()
        msg.reply_text = AsyncMock()
        ctx = make_context({
            "nueva_date":    TEST_DATE,
            "nueva_nombre":  TEST_APT_NAME,
            "nueva_hora":    TEST_APT_TIME,
            "nueva_tipo":    "trabajo",
            "nueva_notas":   "",
            "nueva_user_id": TEST_USER_ID,
        })
        result = await _save_appointment(msg, ctx)
        assert result == NUEVA_CONFLICT


@pytest.mark.asyncio
async def test_get_appointments_con_user_id(mock_api):
    """cmd_citas llama a get_appointments con user_id del update."""
    with patch("src.bot.handlers.citas.api", mock_api):
        from src.bot.handlers.citas import cmd_citas
        update = make_update_callback("citas_nav_" + TEST_DATE)
        ctx    = make_context()
        await cmd_citas(update, ctx)
        mock_api.get_appointments.assert_awaited_once_with(TEST_DATE, TEST_USER_ID)
