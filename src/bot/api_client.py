# src/bot/api_client.py
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


async def create_appointment(time: str, type_: str, notes: str = "") -> dict:
    today = date.today().isoformat()
    data = {"time": time, "type": type_, "notes": notes}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/appointments/{today}", json=data)
        r.raise_for_status()
        return r.json()


async def log_habit(habit: str, value: str) -> dict:
    today = date.today().isoformat()
    data = {"habit": habit, "value": value}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/habits/{today}", json=data)
        r.raise_for_status()
        return r.json()
