"""
Tests unitarios para src/bot/utils/dates.py

Cubre:
 - _parse_date_flex: hoy/mañana/ayer, formato ISO, dateparser, inválido
 - _parse_date_arg: con/sin argumento
 - _date_label: etiquetas hoy/mañana/ayer/otra fecha
 - _date_short: formato corto
 - _greeting: por tramos horarios
 - _monday: lunes de la semana
"""

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from src.bot.utils.dates import (
    _date_label,
    _date_short,
    _greeting,
    _monday,
    _parse_date_arg,
    _parse_date_flex,
)


# ────────────────────────────────────────────────────────────────
class TestParseDateFlex:
    def test_hoy(self):
        assert _parse_date_flex("hoy") == str(date.today())

    def test_today_en(self):
        assert _parse_date_flex("today") == str(date.today())

    def test_manana(self):
        expected = str(date.today() + timedelta(days=1))
        assert _parse_date_flex("mañana") == expected

    def test_manana_sin_tilde(self):
        expected = str(date.today() + timedelta(days=1))
        assert _parse_date_flex("manana") == expected

    def test_ayer(self):
        expected = str(date.today() - timedelta(days=1))
        assert _parse_date_flex("ayer") == expected

    def test_iso_format(self):
        assert _parse_date_flex("2026-04-15") == "2026-04-15"

    def test_iso_formato_invalido(self):
        assert _parse_date_flex("texto basura") is None

    def test_mayusculas_normalizadas(self):
        assert _parse_date_flex("HOY") == str(date.today())

    def test_espacios_extra(self):
        assert _parse_date_flex("  hoy  ") == str(date.today())


class TestParseDateArg:
    def test_con_argumento_valido(self):
        assert _parse_date_arg("hoy") == str(date.today())

    def test_sin_argumento_devuelve_hoy(self):
        assert _parse_date_arg(None) == str(date.today())

    def test_argumento_invalido_devuelve_hoy(self):
        assert _parse_date_arg("textobasura!!!") == str(date.today())


class TestDateLabel:
    def test_hoy(self):
        label = _date_label(str(date.today()))
        assert label.startswith("hoy")

    def test_manana(self):
        tomorrow = str(date.today() + timedelta(days=1))
        assert _date_label(tomorrow).startswith("mañana")

    def test_ayer(self):
        yesterday = str(date.today() - timedelta(days=1))
        assert _date_label(yesterday).startswith("ayer")

    def test_otra_fecha_no_tiene_prefijo_relativo(self):
        other = "2025-01-15"
        label = _date_label(other)
        assert "hoy" not in label and "mañana" not in label

    def test_formato_contiene_dia_y_mes(self):
        label = _date_label("2026-04-15")
        assert "15" in label


class TestDateShort:
    def test_contiene_dia_numerico(self):
        short = _date_short("2026-04-15")
        assert "15" in short

    def test_contiene_mes_abreviado(self):
        short = _date_short("2026-04-15")
        assert "abr" in short

    def test_contiene_dia_semana(self):
        short = _date_short("2026-04-13")  # Lunes
        assert "Lun" in short


class TestGreeting:
    @pytest.mark.parametrize("hour,expected", [
        (7,  "🌅 Buenos días"),
        (13, "🌅 Buenos días"),
        (14, "🌆 Buenas tardes"),
        (21, "🌆 Buenas tardes"),
        (22, "🌙 Buenas noches"),
        (2,  "🌙 Buenas noches"),
    ])
    def test_greeting_por_hora(self, hour, expected):
        with patch("src.bot.utils.dates.datetime") as mock_dt:
            mock_dt.now.return_value.hour = hour
            assert _greeting() == expected


class TestMonday:
    def test_lunes_devuelve_si_mismo(self):
        assert _monday("2026-04-13") == "2026-04-13"  # Lunes

    def test_miercoles_devuelve_lunes(self):
        assert _monday("2026-04-15") == "2026-04-13"  # Mié → Lun

    def test_domingo_devuelve_lunes_anterior(self):
        assert _monday("2026-04-19") == "2026-04-13"  # Dom → Lun
