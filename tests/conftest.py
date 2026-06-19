"""
Fixtures globales para todos los tests de THDORA.
Usa pytest-asyncio + unittest.mock para aislar ThdoraApiClient de la red real.
"""
from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Event loop ──────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Constantes de test ──────────────────────────────────────────
TEST_USER_ID  = 123456789
TEST_DATE     = str(date.today())
TEST_HABIT    = "Agua"
TEST_VALUE    = "2L"
TEST_APT_NAME = "Reunión equipo"
TEST_APT_TIME = "10:00"


# ── Mock ThdoraApiClient ─────────────────────────────────────────
@pytest.fixture
def mock_api():
    """Mock completo de ThdoraApiClient con respuestas por defecto razonables."""
    api = MagicMock()

    # Habits
    api.get_habits      = AsyncMock(return_value={TEST_HABIT: TEST_VALUE})
    api.log_habit       = AsyncMock(return_value={"habit": TEST_HABIT, "value": TEST_VALUE})
    api.update_habit    = AsyncMock(return_value={"habit": TEST_HABIT, "value": "3L"})
    api.delete_habit    = AsyncMock(return_value=True)
    api.get_habit_config = AsyncMock(return_value=None)  # sin config especial
    api.get_habit_stats = AsyncMock(return_value=[])

    # Habit config
    api.get_habit_configs   = AsyncMock(return_value=[])
    api.upsert_habit_config = AsyncMock(return_value={"name": TEST_HABIT})
    api.delete_habit_config = AsyncMock(return_value=True)

    # Appointments
    api.get_appointments = AsyncMock(return_value=[
        {"name": TEST_APT_NAME, "time": TEST_APT_TIME, "type": "trabajo", "notes": ""}
    ])
    api.create_appointment = AsyncMock(return_value={
        "name": TEST_APT_NAME, "time": TEST_APT_TIME
    })
    api.update_appointment = AsyncMock(return_value={
        "name": TEST_APT_NAME, "time": "11:00"
    })
    api.delete_appointment = AsyncMock(return_value=True)

    # User config
    api.get_user_config    = AsyncMock(return_value={
        "daily_summary_enabled": True,
        "notif_enabled": True,
        "evening_log_enabled": True,
        "notif_time": "08:00",
        "evening_log_time": "21:00",
        "notif_offset_minutes": 15,
    })
    api.update_user_config = AsyncMock(return_value={
        "daily_summary_enabled": False,
    })

    # Summary
    api.get_summary = AsyncMock(return_value={"habits": {}, "appointments": []})

    return api


# ── Fake PTB objects ────────────────────────────────────────────────

def make_user(user_id: int = TEST_USER_ID):
    u = MagicMock()
    u.id       = user_id
    u.username = "testuser"
    u.first_name = "Test"
    return u


def make_message(text: str = "", user_id: int = TEST_USER_ID):
    msg = MagicMock()
    msg.text          = text
    msg.from_user     = make_user(user_id)
    msg.reply_text    = AsyncMock()
    msg.effective_user = make_user(user_id)
    return msg


def make_callback_query(data: str, user_id: int = TEST_USER_ID):
    q = MagicMock()
    q.data        = data
    q.from_user   = make_user(user_id)
    q.answer      = AsyncMock()
    q.edit_message_text         = AsyncMock()
    q.edit_message_reply_markup = AsyncMock()
    q.message     = make_message(user_id=user_id)
    return q


def make_update_message(text: str = "", user_id: int = TEST_USER_ID):
    update = MagicMock()
    update.message         = make_message(text, user_id)
    update.effective_user  = make_user(user_id)
    update.callback_query  = None
    return update


def make_update_callback(data: str, user_id: int = TEST_USER_ID):
    update = MagicMock()
    update.callback_query  = make_callback_query(data, user_id)
    update.effective_user  = make_user(user_id)
    update.message         = None
    return update


def make_context(user_data: dict | None = None):
    ctx = MagicMock()
    ctx.user_data = user_data or {}
    ctx.bot       = AsyncMock()
    ctx.args      = []
    return ctx


# Exportar helpers como fixtures también
@pytest.fixture
def user_id():
    return TEST_USER_ID

@pytest.fixture
def today():
    return TEST_DATE
