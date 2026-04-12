"""
Tests unitarios para src/bot/utils/accum.py

Cubre:
 - _accumulate_value: acumulación, sobreescritura, unidades, casos borde
 - _clean_acum_context: limpia user_data
"""

from unittest.mock import MagicMock

import pytest

from src.bot.utils.accum import _accumulate_value, _clean_acum_context


class TestAccumulateValue:
    def test_sobreescritura_sin_prefijo(self):
        assert _accumulate_value("5h", "8h") == "8h"

    def test_acumulacion_simple(self):
        assert _accumulate_value("5", "+3") == "8"

    def test_acumulacion_con_unidad(self):
        assert _accumulate_value("30min", "+15min") == "45min"

    def test_acumulacion_sin_existing(self):
        assert _accumulate_value(None, "+2") == "2"

    def test_acumulacion_float(self):
        result = _accumulate_value("1.5", "+0.5")
        assert result == "2"

    def test_acumulacion_litros(self):
        assert _accumulate_value("1L", "+0.5L") == "1.5L"

    def test_hereda_unidad_de_existing(self):
        # +2 sin unidad, existing tiene 'h' → hereda 'h'
        result = _accumulate_value("6h", "+2")
        assert result == "8h"

    def test_unidad_nueva_prevalece_sobre_existing(self):
        result = _accumulate_value("6h", "+2min")
        assert result == "8min"

    def test_existing_invalido_usa_incremento(self):
        result = _accumulate_value("no_numerico", "+5")
        assert result == "5"

    def test_nuevo_valor_sin_prefijo_mas(self):
        # Sin '+' → sobreescritura directa
        assert _accumulate_value("10", "7") == "7"

    def test_acumulacion_entero_grande(self):
        assert _accumulate_value("1000", "+500") == "1500"

    def test_existing_none_sobreescritura(self):
        assert _accumulate_value(None, "nuevo") == "nuevo"


class TestCleanAccumContext:
    def test_elimina_claves(self):
        ctx = MagicMock()
        ctx.user_data = {"acum_hab_date": "2026-04-12", "acum_hab_nombre": "sueño", "otra": "x"}
        _clean_acum_context(ctx)
        assert "acum_hab_date"   not in ctx.user_data
        assert "acum_hab_nombre" not in ctx.user_data
        assert ctx.user_data["otra"] == "x"  # no toca otras claves

    def test_tolerante_si_no_existen(self):
        ctx = MagicMock()
        ctx.user_data = {}
        _clean_acum_context(ctx)  # no debe lanzar
