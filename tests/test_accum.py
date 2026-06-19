"""
Tests unitarios de _accumulate_value.
Casos: acumular numérico, tiempo, sobreescribir, None base, prefijo '+' sin base.
"""
from __future__ import annotations

import pytest


def accumulate(existing, new_input):
    from src.bot.utils.accum import _accumulate_value
    return _accumulate_value(existing, new_input)


def test_acumular_numerico_entero():
    assert accumulate("2", "+3") == "5"


def test_acumular_con_unidad_L():
    """'1L' + '+1L' = '2L'"""
    result = accumulate("1L", "+1L")
    assert "2" in result


def test_acumular_con_unidad_min():
    result = accumulate("30min", "+15min")
    assert "45" in result


def test_sobreescribir_sin_prefijo():
    """Sin '+' debe sobreescribir directamente."""
    assert accumulate("2L", "5L") == "5L"


def test_acumular_con_base_none():
    """Base None: el resultado debe ser el nuevo valor."""
    result = accumulate(None, "+3")
    assert "3" in str(result)


def test_acumular_flotante():
    result = accumulate("1.5", "+0.5")
    assert "2" in result


def test_input_directo_sin_base():
    """Sin base existente y sin '+', devuelve el valor tal cual."""
    assert accumulate(None, "8h") == "8h"
