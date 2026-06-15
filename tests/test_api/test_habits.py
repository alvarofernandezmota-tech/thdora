# tests/test_api/test_habits.py
import pytest

TEST_USER_ID = 123456789
TEST_DATE = "2026-06-15"

@pytest.mark.asyncio
async def test_get_habits_returns_list(app_client):
    response = await app_client.get(f"/habits/{TEST_DATE}?user_id={TEST_USER_ID}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))

@pytest.mark.asyncio
async def test_log_habit_ok(app_client):
    response = await app_client.post(
        f"/habits/{TEST_DATE}?user_id={TEST_USER_ID}",
        json={"habit": "sueño", "value": "8h"}
    )
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["habit"] == "sueño"
    assert data["value"] == "8h"

@pytest.mark.asyncio
async def test_log_habit_missing_user_id(app_client):
    response = await app_client.post(
        f"/habits/{TEST_DATE}",
        json={"habit": "sueño", "value": "8h"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_habit_ok(app_client):
    response = await app_client.delete(f"/habits/{TEST_DATE}/sue%C3%B1o?user_id={TEST_USER_ID}")
    assert response.status_code in [200, 204]
