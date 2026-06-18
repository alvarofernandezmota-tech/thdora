"""
Callback handler para la desambiguación de citas via botones inline.

Se activa cuando el usuario pulsa uno de los botones generados por
nlp_handler al detectar múltiples citas candidatas.

callback_data formato:
    'nlp_disambig|<action>|<id>|<date>|<index>'

Donde:
    action → 'borrar_cita' o 'editar_cita'
    id     → ID real de la cita en la BD
    date   → fecha YYYY-MM-DD de la cita
    index  → índice de la cita en esa fecha
"""

import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards import _kb_start
from src.bot.handlers.nlp import _invalidate_cache, _build_day_schedule, _time_to_min

logger = logging.getLogger(__name__)

# ThdoraApiClient lazy — se instancia solo en la primera llamada al handler
_api = None


def _get_api():
    global _api
    if _api is None:
        from src.bot.api_client import ThdoraApiClient
        _api = ThdoraApiClient()
    return _api


_DEFAULT_DURATION_MIN = 60


def _end_time(start: str, duration: int = _DEFAULT_DURATION_MIN) -> str:
    total = _time_to_min(start) + duration
    return f"{total // 60:02d}:{total % 60:02d}"


async def cb_nlp_disambig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la elección del usuario tras la desambiguación.
    Ejecuta la acción (borrar o editar) con la cita seleccionada.
    """
    query = update.callback_query
    await query.answer()

    parts = query.data.split("|")
    if len(parts) != 5:
        await query.edit_message_text("❌ Datos inválidos. Inténtalo de nuevo.")
        return

    _, action, cita_id_str, cita_date, index_str = parts

    try:
        cita_id    = int(cita_id_str)
        cita_index = int(index_str)
    except ValueError:
        await query.edit_message_text("❌ Error procesando la selección.")
        return

    today = date.today().isoformat()
    api = _get_api()

    # ── borrar_cita ──────────────────────────────────────────────────────────────
    if action == "borrar_cita":
        try:
            ok = await api.delete_appointment(date_str=cita_date, index=cita_index)
            if ok:
                _invalidate_cache(context.user_data)
                await query.edit_message_text(
                    f"✅ Cita del *{cita_date}* eliminada.",
                    parse_mode="Markdown",
                )
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="¿Algo más en lo que pueda ayudarte?",
                    reply_markup=_kb_start(),
                )
            else:
                await query.edit_message_text(
                    f"⚠️ No encontré la cita en {cita_date}. Usa /citas para verlas."
                )
        except Exception as e:
            logger.error("Error borrando cita desde disambig: %s", e)
            await query.edit_message_text(
                f"❌ No pude borrar la cita ({e}).\nUsa /citas para gestionarlas."
            )
        return

    # ── editar_cita ──────────────────────────────────────────────────────────────
    if action == "editar_cita":
        pending = context.user_data.pop("nlp_pending_changes", {})
        new_time  = pending.get("new_time")  or None
        new_name  = pending.get("new_name")  or None
        new_type  = pending.get("new_type")  or None
        new_notes = pending.get("new_notes") or None

        if new_time == "00:00" or (not new_time and not new_name and not new_type and not new_notes):
            try:
                citas_del_dia = await api.get_appointments(cita_date)
            except Exception:
                citas_del_dia = []
            schedule = _build_day_schedule(citas_del_dia, cita_date)
            await query.edit_message_text(
                f"⏰ ¿A qué hora quieres mover la cita del *{cita_date}*?\n\n{schedule}",
                parse_mode="Markdown",
            )
            return

        try:
            await api.update_appointment(
                date_str=cita_date, index=cita_index,
                time=new_time, name=new_name, apt_type=new_type, notes=new_notes,
            )
            _invalidate_cache(context.user_data)
            cambios = []
            if new_time:  cambios.append(f"hora → {new_time}")
            if new_name:  cambios.append(f"nombre → {new_name}")
            if new_type:  cambios.append(f"tipo → {new_type}")
            if new_notes: cambios.append("notas actualizadas")
            cambios_str = ", ".join(cambios) or "sin cambios detectados"
            await query.edit_message_text(
                f"✅ Cita del *{cita_date}* actualizada: {cambios_str}.",
                parse_mode="Markdown",
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="¿Algo más en lo que pueda ayudarte?",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error editando cita desde disambig: %s", e)
            await query.edit_message_text(
                f"❌ No pude editar la cita ({e}).\nUsa /citas para gestionarlas."
            )
        return

    await query.edit_message_text("❌ Acción desconocida.")
