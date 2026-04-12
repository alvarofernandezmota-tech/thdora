"""
Helpers de acumulación de valores para hábitos.
"""

import re
from typing import Optional

from telegram.ext import ContextTypes

_RE_ACUM   = re.compile(r"^\+([\d\.]+)(.*)$")
_RE_NUMBER = re.compile(r"^([\d\.]+)(.*)$")


def _accumulate_value(existing: Optional[str], new_input: str) -> str:
    m_new = _RE_ACUM.match(new_input.strip())
    if not m_new:
        return new_input
    increment = float(m_new.group(1))
    unit = m_new.group(2).strip()
    if existing:
        m_old = _RE_NUMBER.match(existing.strip())
        if m_old:
            try:
                base     = float(m_old.group(1))
                old_unit = m_old.group(2).strip()
                unit     = unit or old_unit
                return f"{base + increment:g}{unit}"
            except ValueError:
                pass
    return f"{increment:g}{unit}"


def _clean_acum_context(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("acum_hab_date",   None)
    context.user_data.pop("acum_hab_nombre", None)
