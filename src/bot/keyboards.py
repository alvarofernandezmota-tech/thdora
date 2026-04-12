"""
Teclados inline del bot THDORA.
Todos los _kb_* y _nav_keyboard centralizados aquí.
"""

from datetime import datetime, timedelta
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.dates import _date_short, _monday

# ── Constantes ────────────────────────────────────────────────────────
TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]

# Franjas horarias: (etiqueta, rango_horas)
FRANJAS = [
    ("🌅 Mañana",  list(range(6, 14))),   # 06:00 – 13:00
    ("🌆 Tarde",   list(range(14, 22))),   # 14:00 – 21:00
    ("🌙 Noche",   list(range(22, 24)) + list(range(0, 6))),  # 22:00 – 05:00
]
FRANJA_KEYS = ["manana", "tarde", "noche"]


def _kb_start():
    from datetime import date
    today = str(date.today())
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Citas hoy",   callback_data=f"citas_nav_{today}"),
            InlineKeyboardButton("📊 Hábitos hoy", callback_data=f"habitos_nav_{today}"),
        ],
        [
            InlineKeyboardButton("📋 Semana", callback_data=f"semana_nav_{_monday(today)}"),
        ],
        [
            InlineKeyboardButton("➕ Nueva cita",   callback_data="quick_nueva"),
            InlineKeyboardButton("➕ Nuevo hábito", callback_data="quick_habito"),
        ],
        [
            InlineKeyboardButton("⚙️ Config", callback_data="quick_config"),
        ],
    ])


def _nav_keyboard(date_str: str, prefix: str) -> InlineKeyboardMarkup:
    """Barra de navegación ◀️ [Fecha real] ▶️ + cambio de vista + 🏠 Menú."""
    d      = datetime.strptime(date_str, "%Y-%m-%d").date()
    prev_d = str(d - timedelta(days=1))
    next_d = str(d + timedelta(days=1))
    center_label = _date_short(date_str)
    other        = "habitos" if prefix == "citas" else "citas"
    other_emoji  = "📊" if prefix == "citas" else "📅"
    if prefix == "citas":
        quick_btn = InlineKeyboardButton("➕ Nueva", callback_data=f"quick_nueva_{date_str}")
    else:
        quick_btn = InlineKeyboardButton("➕ Nuevo", callback_data=f"quick_habito_{date_str}")
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️",         callback_data=f"{prefix}_nav_{prev_d}"),
            InlineKeyboardButton(center_label, callback_data=f"{prefix}_nav_{date_str}"),
            InlineKeyboardButton("▶️",         callback_data=f"{prefix}_nav_{next_d}"),
        ],
        [
            quick_btn,
            InlineKeyboardButton(f"{other_emoji} {other.capitalize()}", callback_data=f"{other}_nav_{date_str}"),
        ],
        [
            InlineKeyboardButton("📋 Semana", callback_data=f"semana_nav_{_monday(date_str)}"),
            InlineKeyboardButton("🏠 Menú",   callback_data="menu_home"),
        ],
    ])


def _kb_back(date_str: str, prefix: str = "citas") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("← Volver al día", callback_data=f"{prefix}_nav_{date_str}"),
        InlineKeyboardButton("🏠 Menú",          callback_data="menu_home"),
    ]])


def _kb_week_nav(monday_str: str) -> InlineKeyboardMarkup:
    from datetime import date
    d      = datetime.strptime(monday_str, "%Y-%m-%d").date()
    prev_w = str(d - timedelta(weeks=1))
    next_w = str(d + timedelta(weeks=1))
    this_w = str(date.today() - timedelta(days=date.today().weekday()))
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️ Semana ant.", callback_data=f"semana_nav_{prev_w}"),
            InlineKeyboardButton("Semana sig. ▶️", callback_data=f"semana_nav_{next_w}"),
        ],
        [
            InlineKeyboardButton("📅 Esta semana", callback_data=f"semana_nav_{this_w}"),
            InlineKeyboardButton("🏠 Menú",         callback_data="menu_home"),
        ],
    ])


def _kb_tipos() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t.capitalize(), callback_data=f"tipo_{t}")] for t in TIPOS_CITA]
    )


def _kb_franjas() -> InlineKeyboardMarkup:
    """Paso 1 de /nueva — elegir franja horaria."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🌅 Mañana",  callback_data="franja_manana"),
        InlineKeyboardButton("🌆 Tarde",   callback_data="franja_tarde"),
        InlineKeyboardButton("🌙 Noche",   callback_data="franja_noche"),
    ], [
        InlineKeyboardButton("✏️ Escribir hora exacta", callback_data="franja_exacta"),
    ]])


def _kb_horas_franja(franja_key: str) -> InlineKeyboardMarkup:
    """Paso 2 — botones de hora en punto según la franja."""
    horas_map = {
        "manana": list(range(6, 14)),   # 06–13
        "tarde":  list(range(14, 22)),  # 14–21
        "noche":  list(range(22, 24)) + list(range(0, 6)),  # 22–23 + 00–05
    }
    horas = horas_map.get(franja_key, list(range(6, 14)))
    rows, row = [], []
    for h in horas:
        label = f"{h:02d}:00"
        row.append(InlineKeyboardButton(label, callback_data=f"hora_punto_{h:02d}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([
        InlineKeyboardButton("🕐 Ver cuartos",       callback_data="hora_ver_cuartos"),
        InlineKeyboardButton("✏️ Escribir exacta",   callback_data="hora_exacta"),
    ])
    return InlineKeyboardMarkup(rows)


def _kb_cuartos(hora: int) -> InlineKeyboardMarkup:
    """Paso 3 — cuartos de hora para la hora seleccionada."""
    cuartos = [0, 15, 30, 45]
    row = [
        InlineKeyboardButton(f"{hora:02d}:{m:02d}", callback_data=f"hora_cuarto_{hora:02d}:{m:02d}")
        for m in cuartos
    ]
    return InlineKeyboardMarkup([row, [
        InlineKeyboardButton("✏️ Escribir exacta", callback_data="hora_exacta"),
    ]])


def _kb_hab_value(cfg: Optional[dict]) -> Optional[InlineKeyboardMarkup]:
    if not cfg:
        return None
    habit_type = cfg.get("habit_type", "text")
    quick_vals = cfg.get("quick_vals", [])
    if habit_type == "boolean":
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí", callback_data="hval_1"),
            InlineKeyboardButton("❌ No", callback_data="hval_0"),
        ]])
    if quick_vals:
        row, rows = [], []
        for val in quick_vals:
            row.append(InlineKeyboardButton(val, callback_data=f"hval_{val}"))
            if len(row) == 3:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        rows.append([InlineKeyboardButton("✏️ Otro valor", callback_data="hval___otro")])
        return InlineKeyboardMarkup(rows)
    return None


def _kb_apt_confirm(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"adc_{date_str}_{index}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_actions(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️", callback_data=f"hd_{date_str}_{h}"),
        InlineKeyboardButton("✏️", callback_data=f"he_{date_str}_{h}"),
        InlineKeyboardButton("➕", callback_data=f"ha_{date_str}_{h}"),
    ]])


def _kb_hab_confirm(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"hdc_{date_str}_{h}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_conflict() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✏️ Sobreescribir", callback_data="hconf_overwrite"),
        InlineKeyboardButton("➕ Sumar",          callback_data="hconf_add"),
        InlineKeyboardButton("❌ Cancelar",       callback_data="hconf_cancel"),
    ]])


def _kb_conflict_apt() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Crear de todas formas", callback_data="aptconf_ok"),
        InlineKeyboardButton("❌ Cambiar hora",          callback_data="aptconf_change"),
    ]])


def _kb_cita_detail(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Editar",  callback_data=f"ae_{date_str}_{index}"),
            InlineKeyboardButton("🗑️ Borrar", callback_data=f"ad_{date_str}_{index}"),
        ],
        [
            InlineKeyboardButton("← Volver al día", callback_data=f"citas_nav_{date_str}"),
        ],
    ])
