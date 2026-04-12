"""
Helpers de fecha para el bot THDORA.
"""

from datetime import date, datetime, timedelta
from typing import Optional

try:
    import dateparser
    _HAS_DATEPARSER = True
except ImportError:
    _HAS_DATEPARSER = False


def _parse_date_flex(text: str) -> Optional[str]:
    t = text.strip().lower()
    if t in ("hoy", "today"):                     return str(date.today())
    if t in ("mañana", "manana", "tomorrow"):     return str(date.today() + timedelta(days=1))
    if t in ("ayer", "yesterday"):                return str(date.today() - timedelta(days=1))
    try:
        datetime.strptime(t, "%Y-%m-%d")
        return t
    except ValueError:
        pass
    if _HAS_DATEPARSER:
        parsed = dateparser.parse(
            text, languages=["es", "en"],
            settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
        )
        if parsed:
            return parsed.strftime("%Y-%m-%d")
    return None


def _parse_date_arg(arg: Optional[str]) -> str:
    if arg:
        r = _parse_date_flex(arg)
        if r:
            return r
    return str(date.today())


def _date_label(date_str: str) -> str:
    today     = str(date.today())
    tomorrow  = str(date.today() + timedelta(days=1))
    yesterday = str(date.today() - timedelta(days=1))
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    months    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
    short = f"{day_names[d.weekday()]} {d.day} {months[d.month-1]}"
    if date_str == today:     return f"hoy — {short}"
    if date_str == tomorrow:  return f"mañana — {short}"
    if date_str == yesterday: return f"ayer — {short}"
    return short


def _date_short(date_str: str) -> str:
    """Etiqueta corta para el botón central de navegación: 'Sáb 28 mar'."""
    d         = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    months    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
    return f"{day_names[d.weekday()]} {d.day} {months[d.month-1]}"


def _greeting() -> str:
    """Saludo contextual según hora del día."""
    hour = datetime.now().hour
    if 6 <= hour < 14:  return "🌅 Buenos días"
    if 14 <= hour < 22: return "🌆 Buenas tardes"
    return "🌙 Buenas noches"


def _monday(date_str: str) -> str:
    """Devuelve el lunes de la semana del date_str dado."""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return str(d - timedelta(days=d.weekday()))
