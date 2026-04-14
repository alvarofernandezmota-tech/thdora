"""
Handler de texto libre — modo Toki.

Flujo completo:
    1. Envía ⏳ Procesando... (feedback inmediato mientras trabaja Groq)
    2. Consulta contexto real de la API:
       — citas de hoy y mañana
       — citas de los próximos 7 días (para consulta_semana)
       — hábitos de hoy
       Si la API falla, el contexto queda vacío y el bot sigue funcionando.
    3. Llama a groq_router.route() con el texto + contexto + username
    4. Según el intent:
       nueva_cita      → crea la cita en la API (con fix hora 00:00)
       borrar_cita     → confirma + borra la cita en la API
       editar_cita     → confirma + edita la cita en la API
       log_habito      → registra el hábito en la API
       borrar_habito   → confirma + borra el hábito en la API
       consulta        → responde con datos reales de hoy/mañana
       consulta_semana → responde con datos de los próximos 7 días
       chat            → respuesta conversacional con contexto
       desconocido     → muestra el menú principal del bot (NO texto suelto)

Diseño Toki:
    La IA actúa solo como router de intención + extractor de slots.
    Cuando no entiende, devuelve siempre la interfaz del bot (botones),
    no una respuesta de texto inventada.
    El contexto real (agenda + hábitos) se inyecta en el prompt antes
    de llamar a Groq, para respuestas tipo ¿qué tengo mañana?
"""

import asyncio
import logging
from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.groq_router import route
from src.bot.keyboards import _kb_start

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()

_MSG_MENU = (
    "🤔 No he entendido bien lo que quieres hacer.\n"
    "Usa los botones o escíbeme algo como:\n"
    "  • _\"mañana dentista a las 5\"_\n"
    "  • _\"dormí 7 horas\"_\n"
    "  • _\"cancela el gym de hoy\"_\n"
    "  • _\"mueve el dentista a las 18\"_"
)

_MSG_HORA_CONFIRM = (
    "⏰ No he detectado la hora. ¿A qué hora es la cita _{name}_?\n"
    "Escíbeme la hora (ej: _17:00_) o usa /nueva para el flujo guiado."
)


async def _get_api_context(today: str, tomorrow: str) -> dict:
    """
    Obtiene el contexto real de la API para inyectar en el prompt de Groq.
    Hace todas las llamadas en paralelo con gather. Si alguna falla, devuelve
    lo que haya podido obtener (degradación elegante).

    Para consulta_semana, también obtiene citas de los próximos 7 días
    y las agrupa en un resumen de texto para el modelo.
    """
    async def _safe(coro):
        try:
            return await coro
        except Exception:
            return None

    # Citas de los próximos 7 días (para consulta_semana)
    week_dates = [
        (date.today() + timedelta(days=i)).isoformat()
        for i in range(1, 7)   # hoy ya está en 'citas', empezamos desde mañana
    ]

    results = await asyncio.gather(
        _safe(api.get_appointments(today)),
        _safe(api.get_appointments(tomorrow)),
        _safe(api.get_habits(today)),
        *[_safe(api.get_appointments(d)) for d in week_dates],
    )

    citas     = results[0] or []
    citas_man = results[1] or []
    habitos   = results[2] or {}
    week_data = results[3:]

    # Construir resumen legible de la semana para el modelo
    semana_lines = []
    for i, day_citas in enumerate(week_data):
        if day_citas:
            day_str = week_dates[i]
            citas_str = ", ".join(
                f"{c.get('time','?')} {c.get('name','?')}" for c in day_citas
            )
            semana_lines.append(f"  {day_str}: {citas_str}")

    citas_semana = "\n".join(semana_lines) if semana_lines else "ninguna"

    return {
        "citas":        citas,
        "citas_manana": citas_man,
        "habitos":      habitos,
        "citas_semana": citas_semana,
    }


async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    today    = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Nombre del usuario para personalizar respuestas THDORA
    username = (
        update.effective_user.first_name
        or update.effective_user.username
        or "Álvaro"
    )

    # 1. Feedback inmediato
    processing_msg = await update.message.reply_text("⏳ Procesando...")

    # 2. Contexto real de la API (paralelo, con semana incluida)
    api_context = await _get_api_context(today, tomorrow)

    # 3. Router NLP con contexto + username
    result = await route(
        text=text,
        user_data=context.user_data,
        api_context=api_context,
        username=username,
    )

    # Borrar ⏳ Procesando...
    try:
        await processing_msg.delete()
    except Exception:
        pass

    intent    = result["intent"]
    data      = result["data"]
    reply     = result["reply"]
    show_menu = result.get("show_menu", False)

    # ── intent desconocido → menú del bot ─────────────────────────────
    if show_menu:
        await update.message.reply_text(
            _MSG_MENU,
            parse_mode="Markdown",
            reply_markup=_kb_start(),
        )
        return

    # ── reply sola (fallo extraccion, chat, consulta) ─────────────────────
    if reply and not data:
        await update.message.reply_text(reply, parse_mode="Markdown")
        return

    # ── nueva_cita ────────────────────────────────────────────────
    if intent == "nueva_cita" and data:
        cita_date  = data.get("date", today)
        cita_time  = data.get("time", "09:00")
        cita_name  = data.get("name", "Cita")
        cita_type  = data.get("type", "otro")
        cita_notes = data.get("notes", "")

        # Fix hora 00:00: pedir confirmación en vez de crear a medianoche
        if cita_time == "00:00":
            await update.message.reply_text(
                _MSG_HORA_CONFIRM.format(name=cita_name),
                parse_mode="Markdown",
            )
            return

        # Conflicto de hora
        conflict = await api.check_appointment_conflict(cita_date, cita_time)
        if conflict:
            await update.message.reply_text(
                f"⚠️ Ya tienes *{conflict.get('name', 'una cita')}* "
                f"el {cita_date} a las {cita_time}.\n"
                f"Elige otra hora o usa /nueva para el flujo guiado.",
                parse_mode="Markdown",
            )
            return

        try:
            await api.create_appointment(
                date_str=cita_date,
                time=cita_time,
                name=cita_name,
                apt_type=cita_type,
                notes=cita_notes,
            )
            await update.message.reply_text(
                f"✅ *{cita_name}* añadida el {cita_date} a las {cita_time} ⌟",
                parse_mode="Markdown",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error creando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude crear la cita ({e}).\nPrueba con /nueva.",
                reply_markup=_kb_start(),
            )
        return

    # ── borrar_cita ────────────────────────────────────────────────
    if intent == "borrar_cita" and data:
        borrar_date = data.get("date", today)
        borrar_idx  = data.get("index", -1)
        borrar_name = data.get("name", "")

        try:
            ok = await api.delete_appointment(date_str=borrar_date, index=borrar_idx)
            if ok:
                await update.message.reply_text(
                    f"✅ *{borrar_name or 'Cita'}* eliminada del {borrar_date}.",
                    parse_mode="Markdown",
                    reply_markup=_kb_start(),
                )
            else:
                await update.message.reply_text(
                    f"⚠️ No encontré esa cita en {borrar_date}. "
                    f"Usa /citas para verlas.",
                    reply_markup=_kb_start(),
                )
        except Exception as e:
            logger.error("Error borrando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude borrar la cita ({e}).\nUsa /citas para gestionarlas.",
                reply_markup=_kb_start(),
            )
        return

    # ── editar_cita ────────────────────────────────────────────────
    if intent == "editar_cita" and data:
        editar_date  = data.get("date", today)
        editar_idx   = data.get("index", -1)
        editar_name  = data.get("name", "Cita")
        new_time     = data.get("new_time") or None
        new_name     = data.get("new_name") or None
        new_type     = data.get("new_type") or None
        new_notes    = data.get("new_notes") or None

        # Fix hora 00:00 en la edicion
        if new_time == "00:00":
            await update.message.reply_text(
                _MSG_HORA_CONFIRM.format(name=editar_name),
                parse_mode="Markdown",
            )
            return

        try:
            updated = await api.update_appointment(
                date_str=editar_date,
                index=editar_idx,
                time=new_time,
                name=new_name,
                apt_type=new_type,
                notes=new_notes,
            )
            # Construir resumen de cambios
            cambios = []
            if new_time:  cambios.append(f"hora → {new_time}")
            if new_name:  cambios.append(f"nombre → {new_name}")
            if new_type:  cambios.append(f"tipo → {new_type}")
            if new_notes: cambios.append(f"notas actualizadas")
            cambios_str = ", ".join(cambios) or "sin cambios detectados"

            await update.message.reply_text(
                f"✅ *{editar_name}* actualizada: {cambios_str}.",
                parse_mode="Markdown",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error editando cita desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude editar la cita ({e}).\nUsa /citas para gestionarlas.",
                reply_markup=_kb_start(),
            )
        return

    # ── log_habito ──────────────────────────────────────────────────
    if intent == "log_habito" and data:
        hab_date  = data.get("date", today)
        hab_name  = data.get("habit", "hábito")
        hab_value = data.get("value", "")

        try:
            await api.log_habit(
                date_str=hab_date,
                habit=hab_name,
                value=hab_value,
            )
            await update.message.reply_text(
                f"✅ *{hab_name}*: {hab_value} — registrado",
                parse_mode="Markdown",
                reply_markup=_kb_start(),
            )
        except Exception as e:
            logger.error("Error registrando hábito desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude registrar el hábito ({e}).\nPrueba con /habito.",
                reply_markup=_kb_start(),
            )
        return

    # ── borrar_habito ───────────────────────────────────────────────
    if intent == "borrar_habito" and data:
        borrar_hab_date = data.get("date", today)
        borrar_hab_name = data.get("habit", "")

        try:
            ok = await api.delete_habit(
                date_str=borrar_hab_date,
                habit=borrar_hab_name,
            )
            if ok:
                await update.message.reply_text(
                    f"✅ *{borrar_hab_name}* eliminado del {borrar_hab_date}.",
                    parse_mode="Markdown",
                    reply_markup=_kb_start(),
                )
            else:
                await update.message.reply_text(
                    f"⚠️ No encontré el hábito *{borrar_hab_name}* en {borrar_hab_date}. "
                    f"Usa /habitos para verlos.",
                    parse_mode="Markdown",
                    reply_markup=_kb_start(),
                )
        except Exception as e:
            logger.error("Error borrando hábito desde NLP: %s", e)
            await update.message.reply_text(
                f"❌ No pude borrar el hábito ({e}).\nUsa /habitos para gestionarlos.",
                reply_markup=_kb_start(),
            )
        return
