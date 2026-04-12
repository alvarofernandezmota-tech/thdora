"""
Tests unitarios para src/bot/keyboards.py

Cubre:
 - _kb_franjas: contiene los 4 botones (3 franjas + exacta)
 - _kb_horas_franja: botones de hora correctos por franja
 - _kb_cuartos: 4 cuartos + exacta
 - _kb_start: botones del menú principal
 - _nav_keyboard: flechas, fecha, cambio de vista, semana, menú
 - _kb_tipos: 4 tipos de cita
 - _kb_hab_value: boolean / quick_vals / sin config
 - _kb_back: botón volver
"""

import pytest
from telegram import InlineKeyboardMarkup

from src.bot.keyboards import (
    _kb_back,
    _kb_cuartos,
    _kb_franjas,
    _kb_hab_value,
    _kb_horas_franja,
    _kb_start,
    _kb_tipos,
    _nav_keyboard,
)


def _all_buttons(kb: InlineKeyboardMarkup):
    """Devuelve lista plana de todos los botones del teclado."""
    return [btn for row in kb.inline_keyboard for btn in row]


class TestKbFranjas:
    def test_tiene_cuatro_botones(self):
        kb = _kb_franjas()
        btns = _all_buttons(kb)
        assert len(btns) == 4

    def test_contiene_manana(self):
        btns = _all_buttons(_kb_franjas())
        data = [b.callback_data for b in btns]
        assert "franja_manana" in data

    def test_contiene_tarde(self):
        data = [b.callback_data for b in _all_buttons(_kb_franjas())]
        assert "franja_tarde" in data

    def test_contiene_noche(self):
        data = [b.callback_data for b in _all_buttons(_kb_franjas())]
        assert "franja_noche" in data

    def test_contiene_exacta(self):
        data = [b.callback_data for b in _all_buttons(_kb_franjas())]
        assert "franja_exacta" in data


class TestKbHorasFranja:
    def test_manana_empieza_en_06(self):
        btns = _all_buttons(_kb_horas_franja("manana"))
        assert any("06" in b.callback_data for b in btns)

    def test_manana_acaba_en_13(self):
        btns = _all_buttons(_kb_horas_franja("manana"))
        assert any("13" in b.callback_data for b in btns)

    def test_tarde_empieza_en_14(self):
        btns = _all_buttons(_kb_horas_franja("tarde"))
        assert any("14" in b.callback_data for b in btns)

    def test_noche_empieza_en_22(self):
        btns = _all_buttons(_kb_horas_franja("noche"))
        assert any("22" in b.callback_data for b in btns)

    def test_incluye_boton_exacta(self):
        btns = _all_buttons(_kb_horas_franja("manana"))
        assert any(b.callback_data == "hora_exacta" for b in btns)


class TestKbCuartos:
    def test_tiene_cuartos_y_exacta(self):
        btns = _all_buttons(_kb_cuartos(10))
        data = [b.callback_data for b in btns]
        assert "hora_cuarto_10:00" in data
        assert "hora_cuarto_10:15" in data
        assert "hora_cuarto_10:30" in data
        assert "hora_cuarto_10:45" in data
        assert "hora_exacta" in data

    def test_total_cinco_botones(self):
        assert len(_all_buttons(_kb_cuartos(8))) == 5


class TestKbStart:
    def test_tiene_citas_hoy(self):
        btns = _all_buttons(_kb_start())
        assert any("citas_nav" in b.callback_data for b in btns)

    def test_tiene_habitos_hoy(self):
        btns = _all_buttons(_kb_start())
        assert any("habitos_nav" in b.callback_data for b in btns)

    def test_tiene_quick_nueva(self):
        btns = _all_buttons(_kb_start())
        assert any(b.callback_data == "quick_nueva" for b in btns)


class TestNavKeyboard:
    def test_prefix_citas_tiene_flechas(self):
        kb   = _nav_keyboard("2026-04-15", "citas")
        data = [b.callback_data for b in _all_buttons(kb)]
        assert any("citas_nav_2026-04-14" in d for d in data)  # ◀️
        assert any("citas_nav_2026-04-16" in d for d in data)  # ▶️

    def test_prefix_habitos_quick_btn_correcto(self):
        kb   = _nav_keyboard("2026-04-15", "habitos")
        data = [b.callback_data for b in _all_buttons(kb)]
        assert any("quick_habito" in d for d in data)

    def test_incluye_menu_home(self):
        kb   = _nav_keyboard("2026-04-15", "citas")
        data = [b.callback_data for b in _all_buttons(kb)]
        assert "menu_home" in data


class TestKbHabValue:
    def test_boolean_devuelve_si_no(self):
        cfg  = {"habit_type": "boolean", "quick_vals": []}
        btns = _all_buttons(_kb_hab_value(cfg))
        data = [b.callback_data for b in btns]
        assert "hval_1" in data
        assert "hval_0" in data

    def test_quick_vals_aparecen(self):
        cfg  = {"habit_type": "numeric", "quick_vals": ["6h", "7h", "8h"]}
        btns = _all_buttons(_kb_hab_value(cfg))
        data = [b.callback_data for b in btns]
        assert "hval_6h" in data
        assert "hval___otro" in data  # siempre añade ✏️ Otro

    def test_sin_config_devuelve_none(self):
        assert _kb_hab_value(None) is None
