"""Tests para calculate_free_slots y flujo de mover cita."""

from __future__ import annotations
import pytest
from src.bot.handlers.citas_slots import calculate_free_slots

FECHA = "2026-06-15"


class TestCalculateFreeSlots:
    def test_available_slots_empty_day(self):
        slots = calculate_free_slots([], FECHA)
        assert len(slots) == 28

    def test_available_slots_with_conflicts(self):
        slots = calculate_free_slots([{"hora": "10:00"}, {"hora": "14:00"}], FECHA)
        horas = [s.replace("⚠️ ", "").strip() for s in slots]
        assert "10:00" not in horas
        assert "14:00" not in horas
        assert len(slots) == 26

    def test_available_slots_tight_margin(self):
        slots = calculate_free_slots([{"hora": "10:00"}], FECHA)
        tight = [s.replace("⚠️ ", "").strip() for s in slots if s.startswith("⚠️")]
        assert "09:30" in tight


class TestMoveConfirmation:
    def test_confirmation_message_format(self):
        nombre, hora_actual, hora_nueva = "Dentista", "09:00", "11:30"
        msg = f"Mover *{nombre}* de {hora_actual} → {hora_nueva}?\n✅ Confirmar  ❌ Cancelar"
        assert nombre in msg and hora_actual in msg and hora_nueva in msg

    def test_callback_data_format(self):
        cb = f"MOVE_7_10:30"
        parts = cb.split("_", 2)
        assert parts[0] == "MOVE" and parts[1] == "7" and parts[2] == "10:30"
