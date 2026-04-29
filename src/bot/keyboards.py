"""
Teclados inline del bot THDORA.

Todos los constructores de InlineKeyboardMarkup centralizados aquí para
desacoplar la lógica de presentación de los handlers. Los handlers sólo
importan las funciones _kb_* y _nav_keyboard que necesitan.

Convención de callback_data:
    citas_nav_{date}         → navegar a día de citas
    habitos_nav_{date}       → navegar a día de hábitos
    semana_nav_{monday}      → navegar a semana
    quick_nueva / quick_habito / quick_config → atajos del menú
    franja_{key}             → selección de franja horaria
    hora_punto_{hh}          → hora exacta en punto
    hora_cuarto_{hh}:{mm}    → hora con cuarto de hora
    hora_ver_cuartos         → mostrar cuartos para la hora seleccionada
    hora_exacta              → pedir hora libre por teclado
    tipo_{tipo}              → tipo de cita
    ae_{date}_{index}        → editar cita
    ad_{date}_{index}        → borrar cita (solicitar confirmación)
    adc_{date}_{index}       → confirmar borrado de cita
    hd_{date}_{habit}        → borrar hábito
    he_{date}_{habit}        → editar hábito
    ha_{date}_{habit}        → añadir entrada de hábito
    hdc_{date}_{habit}       → confirmar borrado de hábito
    hval_{value}             → valor quick para hábito
    cfg_*                    → menús de configuración
    notif_*                  → acciones de notificaciones
    noop_separator           → botón separador visual (sin acción)
    cancel_action            → cancelar acción en curso
    menu_home                → volver al menú principal

Fixes v0.16.2 (2026-04-27):
    - B-NEW6: _kb_horas_franja('noche') separa 22-23 de 00-05 con separador
      visual '-- Madrugada --' para evitar confusión horaria.
    - B-NEW3: _kb_hab_actions y _kb_hab_confirm eliminan el truncado [:15]
      en el nombre del hábito para que la API lo localice correctamente.
"""

from datetime import datetime, timedelta
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.dates import _date_short, _monday

# ── Constantes públicas ──────────────────────────────────────────────────────

TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]
"""Tipos de cita aceptados por la API."""

FRANJAS = [
    ("🌅 Mañana",  list(range(6, 14))),
    ("🏆 Tarde",   list(range(14, 22))),
    ("🌙 Noche",   list(range(22, 24)) + list(range(0, 6))),
]
"""Definición de franjas horarias: (etiqueta, lista de horas)."""

FRANJA_KEYS = ["manana", "tarde", "noche"]
"""Claves internas de las franjas, en el mismo orden que FRANJAS."""

HABIT_TYPE_EMOJIS = {
    "numeric": "🔢",
    "time":    "⏱️",
    "boolean": "✅",
    "text":    "📝",
}
"""Emojis asociados a cada tipo de hábito (usado en vistas de config)."""


# ── Menú principal ───────────────────────────────────────────────────────────

def _kb_start() -> InlineKeyboardMarkup:
    """Teclado del menú principal (/start y /menu).

    Muestra accesos directos a citas y hábitos de hoy, vista semanal,
    creación rápida de cita/hábito y configuración.
    La fecha embebida en los callback_data es siempre la del día actual.

    Returns:
        InlineKeyboardMarkup con 4 filas: [Citas hoy / Hábitos hoy],
        [Semana], [Nueva cita / Nuevo hábito], [Config].
    """
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


# ── Navegación diaria ────────────────────────────────────────────────────────

def _nav_keyboard(date_str: str, prefix: str) -> InlineKeyboardMarkup:
    """Barra de navegación ◀️ [Fecha real] ▶️ + cambio de vista + 🏠 Menú.

    Construye la barra de navegación común a las vistas de citas y hábitos.
    El botón central muestra la fecha formateada (ej: 'Hoy', 'Mañ.', 'Lun 28').

    Args:
        date_str: Fecha del día visible en formato YYYY-MM-DD.
        prefix:   Vista activa: 'citas' o 'habitos'. Determina el botón
                  de cambio de vista y el quick button de creación.

    Returns:
        InlineKeyboardMarkup con 3 filas: [◀️ fecha ▶️],
        [Nuevo / Vista alternativa], [Semana / Menú].
    """
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
    """Botón simple para volver al día + Menú.

    Usado tras acciones puntuales (confirmación de borrado, error, etc.)
    donde sólo se necesita volver atrás sin la barra completa de navegación.

    Args:
        date_str: Fecha destino del botón de vuelta (YYYY-MM-DD).
        prefix:   Vista destino: 'citas' o 'habitos'.

    Returns:
        InlineKeyboardMarkup con una fila: [← Volver al día / 🏠 Menú].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("← Volver al día", callback_data=f"{prefix}_nav_{date_str}"),
        InlineKeyboardButton("🏠 Menú",          callback_data="menu_home"),
    ]])


def _kb_week_nav(monday_str: str) -> InlineKeyboardMarkup:
    """Teclado de navegación semanal (◀️ semana ant. / semana sig. ▶️).

    Args:
        monday_str: Lunes de la semana visible en formato YYYY-MM-DD.

    Returns:
        InlineKeyboardMarkup con 2 filas: [Sem. ant. / Sem. sig.],
        [Esta semana / Menú].
    """
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


# ── Citas — selección de tipo y franja ──────────────────────────────────────

def _kb_tipos() -> InlineKeyboardMarkup:
    """Teclado de selección de tipo de cita.

    Genera un botón por cada tipo en TIPOS_CITA con callback_data 'tipo_{tipo}'.

    Returns:
        InlineKeyboardMarkup con una fila por tipo: Médica, Personal,
        Trabajo, Otra.
    """
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t.capitalize(), callback_data=f"tipo_{t}")] for t in TIPOS_CITA]
    )


def _kb_franjas() -> InlineKeyboardMarkup:
    """Teclado de selección de franja horaria para una cita nueva.

    Muestra los tres bloques: Mañana (06-13), Tarde (14-21), Noche (22-05),
    más la opción de escribir la hora exacta directamente.

    Returns:
        InlineKeyboardMarkup con 2 filas: [Mañana / Tarde / Noche],
        [Escribir hora exacta].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🌅 Mañana",  callback_data="franja_manana"),
        InlineKeyboardButton("🏆 Tarde",   callback_data="franja_tarde"),
        InlineKeyboardButton("🌙 Noche",   callback_data="franja_noche"),
    ], [
        InlineKeyboardButton("✏️ Escribir hora exacta", callback_data="franja_exacta"),
    ]])


def _kb_horas_franja(franja_key: str) -> InlineKeyboardMarkup:
    """Teclado de horas en punto para la franja seleccionada.

    FIX B-NEW6 (v0.16.2): la franja 'noche' mezcla horas de tarde-noche
    (22-23) con madrugada (00-05). Ahora genera dos bloques separados
    por una fila separadora visual para evitar confusión al usuario.

    Args:
        franja_key: 'manana', 'tarde' o 'noche'.

    Returns:
        InlineKeyboardMarkup con botones hora_punto_{hh} organizados
        en filas de 4, más [Ver cuartos / Escribir exacta] al final.
        Para 'noche': bloque 22-23 + separador '-- Madrugada --' + 00-05.
    """
    rows = []

    if franja_key == "noche":
        # Bloque 1: 22:00 y 23:00
        fila_noche = [
            InlineKeyboardButton(f"{h:02d}:00", callback_data=f"hora_punto_{h:02d}")
            for h in [22, 23]
        ]
        rows.append(fila_noche)
        # Separador visual (botón informativo sin acción útil)
        rows.append([InlineKeyboardButton("── Madrugada ──", callback_data="noop_separator")])
        # Bloque 2: 00:00 – 05:00 (4 por fila)
        madrugada = list(range(0, 6))
        row: list = []
        for h in madrugada:
            row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"hora_punto_{h:02d}"))
            if len(row) == 4:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
    else:
        horas_map = {
            "manana": list(range(6, 14)),
            "tarde":  list(range(14, 22)),
        }
        horas = horas_map.get(franja_key, list(range(6, 14)))
        row = []
        for h in horas:
            row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"hora_punto_{h:02d}"))
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
    """Teclado de cuartos de hora para una hora en punto dada.

    Muestra HH:00, HH:15, HH:30, HH:45 en una sola fila.

    Args:
        hora: Hora (0-23) para la que se generan los cuartos.

    Returns:
        InlineKeyboardMarkup con una fila de 4 cuartos más
        [Escribir exacta].
    """
    cuartos = [0, 15, 30, 45]
    row = [
        InlineKeyboardButton(f"{hora:02d}:{m:02d}", callback_data=f"hora_cuarto_{hora:02d}:{m:02d}")
        for m in cuartos
    ]
    return InlineKeyboardMarkup([row, [
        InlineKeyboardButton("✏️ Escribir exacta", callback_data="hora_exacta"),
    ]])


def _kb_conflict_apt() -> InlineKeyboardMarkup:
    """Teclado de resolución de conflicto de solapamiento de citas.

    Se muestra cuando una nueva cita solapa con una existente en la misma
    franja. El usuario puede crear de todas formas o cambiar la hora.

    Returns:
        InlineKeyboardMarkup con [Crear de todas formas / Cambiar hora].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Crear de todas formas", callback_data="aptconf_ok"),
        InlineKeyboardButton("❌ Cambiar hora",          callback_data="aptconf_change"),
    ]])


def _kb_cita_detail(date_str: str, index: int) -> InlineKeyboardMarkup:
    """Teclado de detalle de una cita individual (editar / borrar / volver).

    Args:
        date_str: Fecha de la cita (YYYY-MM-DD).
        index:    Índice de la cita en el listado del día (posición ordinal).

    Returns:
        InlineKeyboardMarkup con [Editar / Borrar] y [← Volver al día].
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Editar",  callback_data=f"ae_{date_str}_{index}"),
            InlineKeyboardButton("🗑️ Borrar", callback_data=f"ad_{date_str}_{index}"),
        ],
        [
            InlineKeyboardButton("← Volver al día", callback_data=f"citas_nav_{date_str}"),
        ],
    ])


def _kb_apt_confirm(date_str: str, index: int) -> InlineKeyboardMarkup:
    """Teclado de confirmación de borrado de cita.

    Se muestra antes de ejecutar el DELETE definitivo para evitar borrados
    accidentales.

    Args:
        date_str: Fecha de la cita (YYYY-MM-DD).
        index:    Índice de la cita a borrar.

    Returns:
        InlineKeyboardMarkup con [Sí, borrar / Cancelar].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"adc_{date_str}_{index}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


# ── Hábitos ───────────────────────────────────────────────────────────────────

def _kb_hab_value(cfg: Optional[dict]) -> Optional[InlineKeyboardMarkup]:
    """Teclado de entrada de valor para un hábito según su tipo y quick_vals.

    Comportamiento por tipo:
    - boolean: botones Sí / No
    - quick_vals configurados: botones de valores predefinidos + 'Otro valor'
    - sin quick_vals: devuelve None (el usuario escribe el valor libremente)

    Args:
        cfg: Configuración del hábito con claves 'habit_type' y 'quick_vals'.
             Puede ser None si el hábito no tiene config guardada.

    Returns:
        InlineKeyboardMarkup con los valores rápidos, o None si no aplica.
    """
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


def _kb_hab_actions(date_str: str, habit: str) -> InlineKeyboardMarkup:
    """Teclado de acciones sobre un registro de hábito existente.

    Muestra los tres botones de acción en una sola fila (borrar/editar/añadir).
    FIX B-NEW3 (v0.16.2): el nombre del hábito se pasa completo — el truncado
    [:15] anterior hacía que la API no encontrara el hábito por nombre.

    Args:
        date_str: Fecha del registro (YYYY-MM-DD).
        habit:    Nombre exacto del hábito tal como lo devuelve la API.

    Returns:
        InlineKeyboardMarkup con [🗑️ / ✏️ / ➕] en una fila.
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️", callback_data=f"hd_{date_str}_{habit}"),
        InlineKeyboardButton("✏️", callback_data=f"he_{date_str}_{habit}"),
        InlineKeyboardButton("➕", callback_data=f"ha_{date_str}_{habit}"),
    ]])


def _kb_hab_confirm(date_str: str, habit: str) -> InlineKeyboardMarkup:
    """Teclado de confirmación de borrado de hábito.

    FIX B-NEW3 (v0.16.2): nombre completo sin [:15].

    Args:
        date_str: Fecha del registro (YYYY-MM-DD).
        habit:    Nombre exacto del hábito.

    Returns:
        InlineKeyboardMarkup con [Sí, borrar / Cancelar].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"hdc_{date_str}_{habit}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_conflict() -> InlineKeyboardMarkup:
    """Teclado de resolución de conflicto cuando ya existe un registro del hábito.

    Se muestra cuando el usuario intenta registrar un hábito que ya tiene
    entrada para ese día. Ofrece tres estrategias de resolución.

    Returns:
        InlineKeyboardMarkup con [Sobreescribir / Sumar / Cancelar].
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✏️ Sobreescribir", callback_data="hconf_overwrite"),
        InlineKeyboardButton("➕ Sumar",          callback_data="hconf_add"),
        InlineKeyboardButton("❌ Cancelar",       callback_data="hconf_cancel"),
    ]])


# ── Config ————————————————————————————————————————————————————————————————

def _kb_config_menu() -> InlineKeyboardMarkup:
    """Menú raíz de /config.

    Returns:
        InlineKeyboardMarkup con [Hábitos], [Notificaciones], [Menú].
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 Hábitos",         callback_data="cfg_habitos")],
        [InlineKeyboardButton("🔔 Notificaciones",  callback_data="cfg_notif")],
        [InlineKeyboardButton("🏠 Menú",            callback_data="menu_home")],
    ])


def _kb_notif_menu(cfg: dict) -> InlineKeyboardMarkup:
    """Menú de notificaciones con estado actual visible en los botones.

    Muestra el estado actual (✅/❌) y la hora configurada directamente en
    la etiqueta de cada botón para que el usuario vea la configuración
    sin necesidad de entrar en un sub-menú.

    Args:
        cfg: Dict de configuración del usuario con claves:
             daily_summary_enabled, daily_summary_time,
             notif_enabled, evening_log_enabled, evening_log_time.

    Returns:
        InlineKeyboardMarkup con un botón por opción de notificación.
    """
    resumen_icon  = "✅" if cfg.get("daily_summary_enabled") else "❌"
    resumen_hora  = cfg.get("daily_summary_time", "08:00")
    aviso_icon    = "✅" if cfg.get("notif_enabled") else "❌"
    evening_icon  = "✅" if cfg.get("evening_log_enabled") else "❌"
    evening_hora  = cfg.get("evening_log_time", "22:00")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{resumen_icon} Resumen diario ({resumen_hora})",
            callback_data="notif_toggle_summary"
        )],
        [InlineKeyboardButton(
            "⏰ Hora resumen",
            callback_data="notif_set_summary_time"
        )],
        [InlineKeyboardButton(
            f"{aviso_icon} Avisos de cita",
            callback_data="notif_toggle_aviso"
        )],
        [InlineKeyboardButton(
            "⏰ Minutos antes de cita",
            callback_data="notif_set_offsets"
        )],
        [InlineKeyboardButton(
            f"{evening_icon} Evening log ({evening_hora})",
            callback_data="notif_toggle_evening"
        )],
        [InlineKeyboardButton(
            "⏰ Hora evening log",
            callback_data="notif_set_evening_time"
        )],
        [InlineKeyboardButton("← Volver", callback_data="cfg_back_menu")],
    ])


def _kb_notif_hora() -> InlineKeyboardMarkup:
    """Teclado para elegir hora de notificación (botones de hora en punto 06-23).

    Usado tanto para la hora del resumen diario como para el evening log.
    Genera filas de 4 botones.

    Returns:
        InlineKeyboardMarkup con botones notif_hora_{hh}:00 + [❌ Cancelar].
    """
    rows, row = [], []
    for h in range(6, 24):
        row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"notif_hora_{h:02d}:00"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Cancelar", callback_data="cfg_notif")])
    return InlineKeyboardMarkup(rows)


def _kb_notif_offsets() -> InlineKeyboardMarkup:
    """Teclado para elegir cuántos minutos antes avisar de una cita.

    Ofrece opciones simples (5/15/30/60 min) y combinadas (15+30, etc.)
    para cubrir los casos de uso más habituales sin requerir entrada libre.

    Returns:
        InlineKeyboardMarkup con un botón por combinación de offsets
        + [❌ Cancelar].
    """
    opciones = [
        ("5 min",  "notif_offsets_5"),
        ("15 min", "notif_offsets_15"),
        ("30 min", "notif_offsets_30"),
        ("60 min", "notif_offsets_60"),
        ("15+30",  "notif_offsets_15,30"),
        ("30+60",  "notif_offsets_30,60"),
        ("15+30+60", "notif_offsets_15,30,60"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in opciones]
    rows.append([InlineKeyboardButton("❌ Cancelar", callback_data="cfg_notif")])
    return InlineKeyboardMarkup(rows)
