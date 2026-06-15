# tests/test_api/test_appointments.py
import pytest

TEST_USER_ID = 123456789
TEST_DATE = "2026-06-15"

@pytest.mark.asyncio
async def test_get_appointments_returns_list(app_client):
    response = await app_client.get(f"/appointments/{TEST_DATE}?user_id={TEST_USER_ID}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Dentista"

@pytest.mark.asyncio
async def test_get_appointments_empty(app_client, mock_manager):
    mock_manager.get_appointments.return_value = []
    response = await app_client.get(f"/appointments/{TEST_DATE}?user_id={TEST_USER_ID}")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_appointment_ok(app_client):
    response = await app_client.post(
        f"/appointments/{TEST_DATE}?user_id={TEST_USER_ID}",
        json={"time": "10:00", "name": "Dentista", "type": "médica", "notes": ""}
    )
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data or "index" in data

@pytest.mark.asyncio
async def test_create_appointment_missing_user_id(app_client):
    response = await app_client.post(
        f"/appointments/{TEST_DATE}",
        json={"time": "10:00", "name": "Dentista", "type": "médica", "notes": ""}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_appointment_ok(app_client):
    response = await app_client.delete(f"/appointments/{TEST_DATE}/1?user_id={TEST_USER_ID}")
    assert response.status_code in [200, 204]

@pytest.mark.asyncio
async def test_delete_appointment_not_found(app_client, mock_manager):
    mock_manager.delete_appointment.return_value = False
    response = await app_client.delete(f"/appointments/{TEST_DATE}/99?user_id={TEST_USER_ID}")
    assert response.status_code == 404
