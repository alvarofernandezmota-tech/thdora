"""
Tests unitarios para las funciones de horario visual del bot.

Cubre las funciones auxiliares de src/bot/handlers/nlp.py:
    - _time_to_min       : conversión 'HH:MM' → minutos
    - _end_time          : cálculo de hora de fin
    - _build_day_schedule: generación del horario visual por franjas

No requiere Telegram ni API. Ejecución::

    pytest tests/unit/bot/test_nlp_schedule.py -v
"""

import pytest

from src.bot.handlers.nlp import _build_day_schedule, _end_time, _time_to_min

_DATE = "2026-04-14"


# ── _time_to_min ──────────────────────────────────────────────────────

class TestTimeToMin:

    def test_medianoche(self) -> None:
        assert _time_to_min("00:00") == 0

    def test_hora_exacta(self) -> None:
        assert _time_to_min("17:00") == 1020

    def test_hora_con_minutos(self) -> None:
        assert _time_to_min("09:30") == 570


# ── _end_time ─────────────────────────────────────────────────────────

class TestEndTime:

    def test_suma_60_minutos(self) -> None:
        assert _end_time("17:00") == "18:00"

    def test_cruza_hora_siguiente(self) -> None:
        assert _end_time("09:30") == "10:30"

    def test_duracion_personalizada(self) -> None:
        assert _end_time("10:00", duration=30) == "10:30"

    def test_formato_con_cero_a_la_izquierda(self) -> None:
        assert _end_time("08:00") == "09:00"


# ── _build_day_schedule ─────────────────────────────────────────────────

class TestBuildDaySchedule:

    def test_dia_vacio_solo_libres(self) -> None:
        """Sin citas, todos los slots deben ser verdes."""
        output = _build_day_schedule([], _DATE)
        assert "🟢" in output
        assert "🔴" not in output
        assert "⚠️" not in output

    def test_limites_08_a_22(self) -> None:
        """El horario siempre empieza a las 08:00 y termina antes de las 22:00."""
        output = _build_day_schedule([], _DATE)
        assert "`08:00`" in output
        assert "`21:30`" in output
        assert "`22:00`" not in output  # la franja de las 22h no se muestra

    def test_cita_marca_dos_slots(self) -> None:
        """Una cita de 60 min a las 10:00 debe marcar 10:00 y 10:30 como ocupados."""
        citas = [{"id": 1, "time": "10:00", "name": "Reunión", "index": 0}]
        output = _build_day_schedule(citas, _DATE)
        lines = output.splitlines()
        line_10 = next(l for l in lines if "`10:00`" in l)
        line_1030 = next(l for l in lines if "`10:30`" in l)
        assert "🔴" in line_10
        assert "🔴" in line_1030
        # El slot siguiente (11:00) debe estar libre
        line_11 = next(l for l in lines if "`11:00`" in l)
        assert "🟢" in line_11

    def test_nombre_aparece_en_primer_slot(self) -> None:
        """El nombre de la cita aparece solo en el primer slot, no en los continuación."""
        citas = [{"id": 1, "time": "10:00", "name": "Dentista", "index": 0}]
        output = _build_day_schedule(citas, _DATE)
        lines = output.splitlines()
        line_10 = next(l for l in lines if "`10:00`" in l)
        line_1030 = next(l for l in lines if "`10:30`" in l)
        assert "Dentista" in line_10
        assert "Dentista" not in line_1030

    def test_highlight_marca_con_advertencia(self) -> None:
        """El slot solicitado en conflicto se marca con ⚠️."""
        citas = [{"id": 1, "time": "17:00", "name": "Dentista", "index": 0}]
        output = _build_day_schedule(citas, _DATE, highlight_time="17:30")
        lines = output.splitlines()
        line_1730 = next(l for l in lines if "`17:30`" in l)
        assert "⚠️" in line_1730

    def test_highlight_en_slot_libre(self) -> None:
        """Si el highlight es una hora libre, también se marca con ⚠️."""
        output = _build_day_schedule([], _DATE, highlight_time="09:00")
        lines = output.splitlines()
        line_9 = next(l for l in lines if "`09:00`" in l)
        assert "⚠️" in line_9

    def test_header_incluye_fecha(self) -> None:
        """El encabezado debe incluir la fecha pasada."""
        output = _build_day_schedule([], _DATE)
        assert _DATE in output

    def test_dos_citas_no_mezclan_slots(self) -> None:
        """Dos citas en horas distintas cada una marca solo sus propios slots."""
        citas = [
            {"id": 1, "time": "09:00", "name": "A", "index": 0},
            {"id": 2, "time": "14:00", "name": "B", "index": 1},
        ]
        output = _build_day_schedule(citas, _DATE)
        lines = output.splitlines()
        line_09  = next(l for l in lines if "`09:00`" in l)
        line_14  = next(l for l in lines if "`14:00`" in l)
        line_11  = next(l for l in lines if "`11:00`" in l)
        assert "🔴" in line_09
        assert "🔴" in line_14
        assert "🟢" in line_11  # franja libre entre las dos citas
