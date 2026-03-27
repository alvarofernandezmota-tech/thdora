import httpx
from datetime import date

BASE_URL = "http://localhost:8000"


async def get_summary() -> dict:
    today = date.today().isoformat()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/summary/{today}")
        r.raise_for_status()
        return r.json()


async def get_appointments() -> list:
    today = date.today().isoformat()
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/appointments/{today}")
        r.raise_for_status()
        return r.json()


async def create_appointment(data: dict) -> dict:
    today = data.get("date", date.today().isoformat())
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/appointments/{today}", json=data)
        r.raise_for_status()
        return r.json()


async def log_habit(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/habits", json=data)
        r.raise_for_status()
        return r.json()
