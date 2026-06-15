# Bot Commands Reference

THDORA uses the `python-telegram-bot` command framework.

## Commands

| Command | Description | Access |
|:---|:---|:---|
| `/start` | Initializes the user session and registers the user in DB | All |
| `/help` | Shows available commands | All |
| `/citas [date]` | Show appointments for a day (default: today) | All |
| `/nueva <date> <time> <name>` | Create a new appointment | All |
| `/borrar <date> <index>` | Delete an appointment by index | All |
| `/habito <name> <value>` | Log a habit for today | All |
| `/habitos [date]` | Show habits for a day | All |
| `/diario [date]` | Daily summary (appointments + habits) | All |
| `/semana [date]` | Weekly summary | All |
| `/reset` | Clears local memory context for the session | All |

## NLP Auto (sin comando)

Mensaje natural → NLP automático via Groq:

```
"nueva cita dentista mañana 10"     → create_appointment
"marcar sueño 7 horas"              → mark_habit_done
"qué tengo hoy"                     → get daily summary
"cita médica el viernes a las 16"   → create_appointment
```

## Usage Examples

**Crear cita:**
```
/nueva 2026-06-16 10:00 Dentista
```

**Ver resumen:**
```
/diario
/diario 2026-06-14
```

**Context Reset:**
```
/reset
→ Flushes local memory buffer for user_id.
```
