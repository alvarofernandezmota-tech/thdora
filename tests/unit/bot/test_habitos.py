"""
Tests unitarios para src/bot/handlers/habitos.py

Cubre:
 - _kb_edit_hab_fields: callback_data contiene nombre completo (fix B-NEW3)
   CONTEXTO B-NEW3: antes se usaba habit[:15] en los callback_data de los
   botones de edición, haciendo que hábitos con nombre >15 chars no pudieran
   encontrarse al parsear el callback de vuelta. Fix en v0.16.2.
"""

import pytest
from telegram import InlineKeyboardMarkup

from src.bot.keyboards import _kb_edit_hab_fields


def _all_buttons(kb: InlineKeyboardMarkup):
    """Devuelve lista plana de todos los botones del teclado."""
    return [btn for row in kb.inline_keyboard for btn in row]


class TestKbEditHabFields:
    """Tests para _kb_edit_hab_fields — fix B-NEW3 (nombre no truncado)."""

    NOMBRE_LARGO = "Meditación matutina"  # 19 chars, > 15
    NOMBRE_CORTO = "Agua"                 # 4 chars

    def test_devuelve_teclado_valido(self):
        """_kb_edit_hab_fields debe devolver un InlineKeyboardMarkup."""
        kb = _kb_edit_hab_fields(self.NOMBRE_CORTO)
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_nombre_largo_no_truncado_en_callback(self):
        """
        B-NEW3: El nombre del hábito NO debe truncarse en los callback_data.
        Antes: habit[:15] hacía que 'Meditación matutina' → 'Meditación mata'
        Ahora: se usa el nombre completo en todos los callbacks.
        """
        kb = _kb_edit_hab_fields(self.NOMBRE_LARGO)
        btns = _all_buttons(kb)
        # Los botones hedit_name_ y hedit_val_ deben tener el nombre completo
        hedit_btns = [
            b for b in btns
            if b.callback_data and b.callback_data.startswith(("hedit_name_", "hedit_val_"))
        ]
        assert len(hedit_btns) > 0, "Deben existir botones hedit_name_ o hedit_val_"
        for btn in hedit_btns:
            assert self.NOMBRE_LARGO in btn.callback_data, (
                f"Nombre truncado en callback_data: '{btn.callback_data}' "
                f"no contiene '{self.NOMBRE_LARGO}'"
            )

    def test_nombre_corto_en_callback(self):
        """Con nombre corto (<15 chars) el callback_data también es correcto."""
        kb = _kb_edit_hab_fields(self.NOMBRE_CORTO)
        btns = _all_buttons(kb)
        hedit_btns = [
            b for b in btns
            if b.callback_data and b.callback_data.startswith(("hedit_name_", "hedit_val_"))
        ]
        for btn in hedit_btns:
            assert self.NOMBRE_CORTO in btn.callback_data

    def test_nombre_exactamente_15_chars(self):
        """Nombre de exactamente 15 chars no debe perderse (límite del bug original)."""
        nombre_15 = "Ejercicio diari"  # exactamente 15 chars
        kb = _kb_edit_hab_fields(nombre_15)
        btns = _all_buttons(kb)
        hedit_btns = [
            b for b in btns
            if b.callback_data and b.callback_data.startswith(("hedit_name_", "hedit_val_"))
        ]
        for btn in hedit_btns:
            assert nombre_15 in btn.callback_data
