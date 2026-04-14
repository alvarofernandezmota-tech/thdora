"""
Tests unitarios para la lógica de solapamiento de citas.

Cubre las funciones auxiliares del router de appointments:
    - _time_to_minutes : conversión 'HH:MM' → minutos
    - _find_overlap    : detección de solapamiento real (duración 60 min)

No requiere API ni base de datos. Ejecución::

    pytest tests/unit/test_appointments_overlap.py -v
"""

import pytest

# Importamos las funciones directamente del router.
# Son helpers puros sin dependencias de FastAPI ni BD.
from src.api.routers.appointments import _find_overlap, _time_to_minutes


# ── Fixtures comunes ──────────────────────────────────────────────────

@pytest.fixture
def cita_17() -> dict:
    """Cita tipo a las 17:00 (ocupa 17:00–18:00)."""
    return {"id": 1, "time": "17:00", "name": "Dentista", "type": "médica", "index": 0}


@pytest.fixture
def cita_10() -> dict:
    """Cita tipo a las 10:00 (ocupa 10:00–11:00)."""
    return {"id": 2, "time": "10:00", "name": "Reunión", "type": "trabajo", "index": 1}


# ── _time_to_minutes ────────────────────────────────────────────────

class TestTimeToMinutes:

    def test_medianoche(self) -> None:
        assert _time_to_minutes("00:00") == 0

    def test_hora_en_punto(self) -> None:
        assert _time_to_minutes("09:00") == 540

    def test_hora_con_minutos(self) -> None:
        assert _time_to_minutes("17:30") == 1050

    def test_ultimo_minuto_del_dia(self) -> None:
        assert _time_to_minutes("23:59") == 1439

    def test_hora_con_cero(self) -> None:
        """Horas y minutos con cero a la izquierda."""
        assert _time_to_minutes("08:05") == 485


# ── _find_overlap ─────────────────────────────────────────────────────

class TestFindOverlap:

    # —— Casos: sin conflicto ——

    def test_dia_vacio_devuelve_none(self) -> None:
        assert _find_overlap([], "17:00") is None

    def test_hora_libre_sin_solapamiento(self, cita_17: dict) -> None:
        """19:00 está fuera del bloque 17:00–18:00."""
        assert _find_overlap([cita_17], "19:00") is None

    def test_cita_contigua_antes_no_solapa(self, cita_17: dict) -> None:
        """16:00–17:00 termina justo cuando empieza la existente → libre."""
        assert _find_overlap([cita_17], "16:00") is None

    def test_cita_contigua_despues_no_solapa(self, cita_17: dict) -> None:
        """18:00–19:00 empieza justo cuando termina la existente → libre."""
        assert _find_overlap([cita_17], "18:00") is None

    def test_multiples_citas_ninguna_solapa(self, cita_17: dict, cita_10: dict) -> None:
        """12:00 está entre 11:00 y 17:00, franja libre."""
        assert _find_overlap([cita_10, cita_17], "12:00") is None

    # —— Casos: con conflicto ——

    def test_hora_exacta_solapa(self, cita_17: dict) -> None:
        """Misma hora que una existente."""
        result = _find_overlap([cita_17], "17:00")
        assert result is not None
        assert result["time"] == "17:00"

    def test_nueva_empieza_dentro_del_bloque(self, cita_17: dict) -> None:
        """17:30 cae dentro del bloque 17:00–18:00."""
        result = _find_overlap([cita_17], "17:30")
        assert result is not None
        assert result["name"] == "Dentista"

    def test_nueva_tapa_inicio_de_existente(self, cita_17: dict) -> None:
        """16:30–17:30 solapa con 17:00–18:00."""
        result = _find_overlap([cita_17], "16:30")
        assert result is not None
        assert result["time"] == "17:00"

    def test_nueva_engloba_completamente_existente(self, cita_17: dict) -> None:
        """16:00–17:00+60 engloba el bloque 17:00–18:00 — NO solapa (empieza a las 16:00 y termina a las 17:00).
        Caso límite: new_end == exist_start → libre."""
        assert _find_overlap([cita_17], "16:00") is None

    def test_devuelve_la_primera_cita_que_solapa(self, cita_10: dict, cita_17: dict) -> None:
        """Con varias citas, devuelve la primera que choca."""
        # 10:30 solapa con cita_10 (10:00–11:00), no con cita_17
        result = _find_overlap([cita_10, cita_17], "10:30")
        assert result is not None
        assert result["id"] == cita_10["id"]

    def test_duracion_personalizada(self) -> None:
        """Con duración de 30 min, 10:30 ya NO solapa con una cita de 10:00."""
        cita = {"id": 1, "time": "10:00", "name": "Breve", "type": "otra", "index": 0}
        # 10:30 == fin de cita de 30 min → contigua, libre
        assert _find_overlap([cita], "10:30", duration=30) is None
        # 10:15 cae dentro del bloque de 30 min → solapa
        assert _find_overlap([cita], "10:15", duration=30) is not None
