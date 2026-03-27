# 🤖 Módulo: `src/bot/`

> **Navegación:** [INDEX](../INDEX.md) · [api.md](api.md) · [core.md](core.md)

Módulo del bot de Telegram. Interfaz de usuario final del sistema THDORA.

---

## Estado actual

| Archivo | Estado | Versión |
|---------|--------|---------|
| `src/bot/__init__.py` | ✅ Completo | 0.5.0 |
| `src/bot/api_client.py` | ✅ Completo | 0.7.0 |
| `src/bot/handlers.py` | ✅ Funcional (mejorable) | 0.7.0 |
| `src/bot/main.py` | ✅ Completo | 0.7.0 |

---

## `api_client.py` — Cliente HTTP

Clase `ThdoraApiClient` que envuelve todas las llamadas a la API FastAPI local.

```python
api = ThdoraApiClient(base_url="http://localhost:8000")
```

### Métodos disponibles

```python
await api.health()                                    # → bool
await api.get_appointments(date_str)                  # → List[dict]
await api.create_appointment(date, time, type, notes) # → dict
await api.delete_appointment(date, index)             # → bool
await api.get_habits(date_str)                        # → Dict[str, str]
await api.log_habit(date, habit, value)               # → dict
await api.get_summary(date_str)                       # → dict
```

### Excepciones

```python
class ApiError(Exception):
    """Se lanza cuando la API devuelve error HTTP o no está disponible."""
```

### Decisión de diseño

- `get_habits` convierte automáticamente la respuesta de lista `[{habit, value}]` a dict `{habit: value}` para simplificar los handlers.
- Timeouts configurables (default: 10s connect, 30s read).
- Logging de todos los errores antes de relanzar `ApiError`.

---

## `handlers.py` — Comandos del bot

### Comandos disponibles

| Comando | Tipo | Descripción |
|---------|------|-------------|
| `/start` | Simple | Presentación y ayuda |
| `/citas [YYYY-MM-DD]` | Simple | Ver citas del día |
| `/nueva` | ConversationHandler | Crear cita (4 pasos) |
| `/borrar <id>` | Simple | Borrar cita por UUID |
| `/habitos [YYYY-MM-DD]` | Simple | Ver hábitos del día |
| `/habito` | ConversationHandler | Registrar hábito (2 pasos) |
| `/resumen [YYYY-MM-DD]` | Simple | Resumen completo del día |
| `/cancelar` | Fallback | Abortar operación en curso |

### Flujo `/nueva` — 4 pasos

```
/nueva
  └─ paso 1: Fecha (YYYY-MM-DD o "hoy")
  └─ paso 2: Hora (HH:MM, 24h)
  └─ paso 3: Tipo → teclado inline (médica/personal/trabajo/otra)
  └─ paso 4: Notas (texto libre o /skip)
       └─ → POST /appointments/{date}
```

### Flujo `/habito` — 2 pasos

```
/habito
  └─ paso 1: Nombre → inline (sueno/THC/tabaco/ejercicio/agua/humor/alimentacion) o texto libre
  └─ paso 2: Valor (8h, 30min, 2L, etc.)
       └─ → POST /habits/{date}
```

### Estados de ConversationHandler

```python
# /nueva  — rango 0-3
NUEVA_DATE, NUEVA_TIME, NUEVA_TYPE, NUEVA_NOTES = range(4)

# /habito — rango 10-11 (separado para evitar colisiones)
HABITO_NOMBRE, HABITO_VALUE = range(10, 12)
```

---

## `main.py` — Entrypoint

```bash
python -m src.bot.main
# o
make run-bot
```

- Lee `BOT_TOKEN` del `.env` vía `load_dotenv()`
- Comprueba salud de la API al arrancar
- Registra todos los handlers y ConversationHandlers
- Inicia `application.run_polling()`

---

## Mejoras planificadas (Fase 7 v2)

- [ ] Fechas flexibles con `dateparser`: `hoy`, `mañana`, `27/03`, `9am`
- [ ] Botones inline en `/citas` y `/habitos` para borrar/editar
- [ ] Hábitos acumulables: `+2L` suma al valor existente
- [ ] Flujo `/nueva` con 5 pasos (añadir nombre/descripción)
- [ ] Edición de citas y hábitos desde la lista

---

_Última actualización: 27 marzo 2026 — 21:00 CET_
