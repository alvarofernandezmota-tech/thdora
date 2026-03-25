"""
Tests unitarios de MemoryLifeManager.

Cubre:
    - create_appointment: creación, UUID único, validación hora y tipo
    - get_appointments: día con citas, día sin citas, aislamiento por día
    - delete_appointment: cita válida, IndexError, día vacío, índice negativo
    - log_habit: registro nuevo, sobreescritura
    - get_habits: día con hábitos, día sin hábitos
    - get_day_summary: estructura completa

Ejecución::

    pytest tests/unit/test_memory_lifemanager.py -v
"""

import pytest
from datetime import date
from uuid import UUID

from src.core.impl.memory_lifemanager import MemoryLifeManager


@pytest.fixture
def mgr() -> MemoryLifeManager:
    """Fixture: instancia limpia de MemoryLifeManager para cada test."""
    return MemoryLifeManager()


@pytest.fixture
def hoy() -> date:
    """Fixture: fecha fija para tests reproducibles."""
    return date(2026, 3, 24)


class TestCreateAppointment:
    """Tests para create_appointment()."""

    def test_retorna_uuid(self, mgr: MemoryLifeManager, hoy: date) -> None:
        result = mgr.create_appointment(hoy, "10:00", "médica")
        assert isinstance(result, UUID)

    def test_ids_unicos(self, mgr: MemoryLifeManager, hoy: date) -> None:
        id1 = mgr.create_appointment(hoy, "10:00", "médica")
        id2 = mgr.create_appointment(hoy, "12:00", "trabajo")
        assert id1 != id2

    def test_cita_se_almacena(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica", "notas")
        citas = mgr.get_appointments(hoy)
        assert len(citas) == 1
        assert citas[0]["type"] == "médica"
        assert citas[0]["time"] == "10:00"
        assert citas[0]["notes"] == "notas"

    def test_multiples_citas_mismo_dia(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        mgr.create_appointment(hoy, "14:00", "trabajo")
        assert len(mgr.get_appointments(hoy)) == 2

    def test_value_error_hora_invalida(self, mgr: MemoryLifeManager, hoy: date) -> None:
        with pytest.raises(ValueError, match="Formato de hora inválido"):
            mgr.create_appointment(hoy, "10h00", "médica")

    def test_value_error_tipo_invalido(self, mgr: MemoryLifeManager, hoy: date) -> None:
        with pytest.raises(ValueError, match="Tipo de cita inválido"):
            mgr.create_appointment(hoy, "10:00", "dentista")


class TestGetAppointments:
    """Tests para get_appointments()."""

    def test_dia_sin_citas_devuelve_lista_vacia(self, mgr: MemoryLifeManager, hoy: date) -> None:
        assert mgr.get_appointments(hoy) == []

    def test_no_mezcla_dias(self, mgr: MemoryLifeManager, hoy: date) -> None:
        manana = date(2026, 3, 25)
        mgr.create_appointment(hoy, "10:00", "médica")
        assert mgr.get_appointments(manana) == []


class TestDeleteAppointment:
    """Tests para delete_appointment()."""

    def test_elimina_cita_valida(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        result = mgr.delete_appointment(hoy, 0)
        assert result is True
        assert mgr.get_appointments(hoy) == []

    def test_elimina_cita_correcta_cuando_hay_multiples(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        mgr.create_appointment(hoy, "14:00", "trabajo")
        mgr.delete_appointment(hoy, 0)
        citas = mgr.get_appointments(hoy)
        assert len(citas) == 1
        assert citas[0]["type"] == "trabajo"

    def test_index_error_indice_invalido(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, 5)

    def test_index_error_dia_vacio(self, mgr: MemoryLifeManager, hoy: date) -> None:
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, 0)

    def test_index_error_indice_negativo(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        with pytest.raises(IndexError):
            mgr.delete_appointment(hoy, -1)


class TestLogHabit:
    """Tests para log_habit()."""

    def test_registra_habito(self, mgr: MemoryLifeManager, hoy: date) -> None:
        result = mgr.log_habit(hoy, "sueno", "8h")
        assert result is True
        assert mgr.get_habits(hoy)["sueno"] == "8h"

    def test_sobreescribe_valor(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.log_habit(hoy, "sueno", "6h")
        mgr.log_habit(hoy, "sueno", "8h")
        assert mgr.get_habits(hoy)["sueno"] == "8h"


class TestGetHabits:
    """Tests para get_habits()."""

    def test_dia_sin_habitos_devuelve_dict_vacio(self, mgr: MemoryLifeManager, hoy: date) -> None:
        assert mgr.get_habits(hoy) == {}


class TestGetDaySummary:
    """Tests para get_day_summary()."""

    def test_estructura_correcta(self, mgr: MemoryLifeManager, hoy: date) -> None:
        summary = mgr.get_day_summary(hoy)
        assert "date" in summary
        assert "appointments" in summary
        assert "habits" in summary

    def test_fecha_en_formato_string(self, mgr: MemoryLifeManager, hoy: date) -> None:
        summary = mgr.get_day_summary(hoy)
        assert summary["date"] == "2026-03-24"

    def test_resumen_incluye_citas_y_habitos(self, mgr: MemoryLifeManager, hoy: date) -> None:
        mgr.create_appointment(hoy, "10:00", "médica")
        mgr.log_habit(hoy, "sueno", "8h")
        summary = mgr.get_day_summary(hoy)
        assert len(summary["appointments"]) == 1
        assert summary["habits"]["sueno"] == "8h"
