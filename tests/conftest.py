# tests/conftest.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from src.api.main import app
from src.api.deps import get_manager

TEST_USER_ID = 123456789
TEST_DATE = "2026-06-15"

@pytest.fixture
def mock_manager():
    m = AsyncMock()
    m.get_appointments.return_value = [
        {"index": 1, "time": "10:00", "name": "Dentista",
         "type": "médica", "notes": "", "date": TEST_DATE}
    ]
    m.create_appointment.return_value = {"id": 1, "index": 1}
    m.delete_appointment.return_value = True
    m.update_appointment.return_value = {"id": 1, "index": 1, "time": "10:00", "name": "Dentista", "type": "médica", "notes": "", "date": TEST_DATE}
    m.get_habits.return_value = {"sueño": "8h", "agua": "2L"}
    m.log_habit.return_value = {"habit": "sueño", "value": "8h"}
    m.delete_habit.return_value = True
    m.get_summary.return_value = {
        "date": TEST_DATE,
        "appointments": [{"time": "10:00", "name": "Dentista", "type": "médica", "notes": ""}],
        "habits": {"sueño": "8h"}
    }
    m.get_week_summary.return_value = {
        TEST_DATE: {"appointments": [], "habits": {"sueño": "8h"}}
    }
    m.get_appointments_range.return_value = []
    m.get_habits_range.return_value = {}
    m.check_appointment_conflict.return_value = None
    return m

@pytest_asyncio.fixture
async def app_client(mock_manager):
    app.dependency_overrides[get_manager] = lambda: mock_manager
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def telegram_update():
    def _make(user_id: int = TEST_USER_ID, text: str = "hola"):
        update = MagicMock()
        update.effective_user.id = user_id
        update.message.text = text
        update.message.reply_text = AsyncMock()
        update.message.delete = AsyncMock()
        update.message.chat.send_action = AsyncMock()
        return update
    return _make

@pytest.fixture
def telegram_context():
    return MagicMock()
