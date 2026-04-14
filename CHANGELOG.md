# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.15.2] — 14 abril 2026 (tarde)

### ✨ NLP v2 — Cache, contexto semana, desambiguación y cierre de proyecto

#### Resumen de sesión
Sesión enfocada en consolidar el NLP de acciones (borrar/editar citas),
aflinar el contexto disponible para el modelo y documentar el proyecto.

---

#### 1. `src/bot/handlers/nlp.py` — Cache TTL + contexto semana completa

- **Cache TTL 2 min** — `_api_context_cache` con timestamp. La API solo se llama
  si han pasado más de 120 s desde el último fetch. Se invalida automáticamente
  al crear, editar o borrar cualquier cita o hábito.
- **Contexto semana completa** — `extract_borrar_cita` y `extract_editar_cita`
  reciben ahora las citas de hoy + mañana + semana completa (`semana_raw`),
  no solo las de hoy. Reduce drasticamente los fallos de desambiguación.

---

#### 2. `src/bot/handlers/nlp_disambig.py` — Nuevo módulo

- `cb_nlp_disambig` — `CallbackQueryHandler` que gestiona la elección del usuario
  cuando hay varias citas candidatas.
- Patrón del callback: `nlp_disambig|<acción>|<apt_id>` (borrar / editar).
- Al pulsar un botón: ejecuta la acción sobre la cita elegida, edita el mensaje
  con confirmación y limpia `nlp_pending_changes` en `user_data`.
- Degradación elegante si la cita ya no existe (404 → aviso amigable).

---

#### 3. `src/bot/main.py` — Registro de cb_nlp_disambig

- Importa `cb_nlp_disambig` desde `handlers.nlp_disambig`.
- Registra `CallbackQueryHandler(cb_nlp_disambig, pattern=r"^nlp_disambig\|")`
  antes de `cancel_action` para evitar colisiones.
- Bump de versión a **v4.2** en docstring.

---

#### 4. `.gitignore` — Protección de datos personales

- Añadido `data/` completo (cubre `thdora.db` y `bot_persistence.pkl`).
- Mantenido `!data/.gitkeep` para que la carpeta exista al clonar.
- **Antes** solo estaba excluido `data/bot_persistence.pkl` — la base de datos
  quedaba desprotegida.

---

#### 5. `ROADMAP.md` — Actualizado

- Sección nueva **"Trabajo inmediato"** con 4 bloques priorizados y tabla de estado.
- F13-v2a marcada como completada.
- Backlog a largo plazo ordenado al final.

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `src/bot/handlers/nlp.py` | ⚡ Cache TTL + contexto semana |
| `src/bot/handlers/nlp_disambig.py` | ✨ Nuevo módulo |
| `src/bot/main.py` | 🔧 Registro cb_nlp_disambig + v4.2 |
| `.gitignore` | 🔒 Protección `data/` completo |
| `ROADMAP.md` | 📝 Bloques priorizados |

### ⚠️ Nota de despliegue
`git pull` + reiniciar bot. No requiere cambios en `.env` ni dependencias.

### ⏩ Siguiente sesión (mañana)
- **Bloque 1.2** — Mostrar horario disponible antes de mover una cita
- Ejercicios Musk de Python (foco por la mañana)

---

## [v0.15.1] — 14 abril 2026

### 🔧 Fix — Conflicto de cita alineado entre API, bot /nueva y editar hora

#### Problema que resuelve
Aunque la API ya detectaba solapamiento real (v0.15.0), el bot mostraba un mensaje
genérico sin información del bloque existente (`⚠️ Ya tienes una cita a las 17:30`).
Además, el flujo de *editar hora* no comprobaba solapamiento en absoluto.

#### Solución
Nuevo helper centralizado `_check_and_show_conflict` que usa el dato devuelto
por la API para montar un mensaje rico y mostrar el horario visual del día.

---

#### `src/bot/handlers/citas.py`

**`_check_and_show_conflict(obj, context, date_str, time_str, is_message)`** — nuevo helper
- Llama a `api.check_appointment_conflict` (solapamiento real, 60 min).
- Si hay conflicto, obtiene nombre y rango de la cita existente:
  `_end_time(ct, 60)` → `Dentista (17:00–18:00)`.
- Obtiene las citas del día y renderiza el horario visual con
  `_build_day_schedule(..., highlight_time=time_str)` (slot solicitado marcado ⚠️).
- Muestra el mensaje con `_kb_conflict_apt()` y retorna `NUEVA_CONFLICT`.
- Degradación elegante: si la API falla, devuelve `None` y el flujo continúa.

**`_after_time_selected`** — simplificado
- Sustituye el bloque `try/except` manual por una llamada a `_check_and_show_conflict`.

**`cb_apt_edit_time`** — nuevo (fix P4)
- Al editar la hora de una cita, ahora comprueba solapamiento antes de guardar.

**`cb_apt_edit_conflict_response`** — nuevo
- Gestiona la respuesta del usuario tras el conflicto en edición.

**`build_edit_apt_handler`** — actualizado
- Añade el estado `NUEVA_CONFLICT` con handler `cb_apt_edit_conflict_response`.

---

### 📦 Archivos modificados en v0.15.1

| Archivo | Cambio |
|---|---|
| `src/bot/handlers/citas.py` | 🔧 Fix + nuevo helper + fix editar hora |
| `CHANGELOG.md` | 📝 Esta entrada |

---

## [v0.15.0] — 14 abril 2026

### ✨ Mejoras de calidad — Solapamiento real, horario visual, rendimiento y tests

#### 1. `src/api/routers/appointments.py` — Conflicto con solapamiento real
- Solapamiento real con duración predeterminada de 60 minutos.
- `_time_to_minutes`, `_find_overlap` con fórmula correcta.
- `check_conflict` acepta `?duration=` como query param.

#### 2. `src/bot/handlers/nlp.py` — Horario visual
- `_build_day_schedule` — franjas de 30 min entre 08:00 y 22:00.
- `_end_time` — calcula hora de fin.

#### 3. `src/bot/handlers/semana.py` — De 14 llamadas a 2 concurrentes
- `asyncio.gather` — de ~14 round-trips en serie a 2 concurrentes (×7 más rápido).

#### 4 & 5. Tests — 32 tests nuevos
- `tests/unit/test_appointments_overlap.py` — 18 tests.
- `tests/unit/bot/test_nlp_schedule.py` — 14 tests.

#### 6. `README.md` — Portfolio-ready
- Badges, stack técnico, arquitectura, decisiones de diseño.

---

## [v0.14.0] — 14 abril 2026

### ✨ Añadido — Modo Toki: contexto real + menú en intent desconocido
- `api_context` inyectado en el system prompt de Groq.
- Intent `desconocido` → menú del bot.

---

## [v0.13.0] — 14 abril 2026
### ✨ Añadido / Mejorado — UX, Persistencia y Personalidad
- `⏳ Procesando...` + fix hora 00:00.
- `PicklePersistence` activa.
- `_CHAT_SYSTEM` reescrito.

---

## [v0.12.0] — 14 abril 2026
- `groq_router.py` completo: clasificador + extractor + chat.
- `handlers/nlp.py` con detección de conflicto.
- `docs/NLP_ARQUITECTURA.md` creado.

---

## [v0.11.0] — 13 abril 2026
- `UserConfig` en SQLite, APScheduler, `/config` con notificaciones.

---

## [v0.10.0] — Abril 2026
- Bot v4 modular + UX avanzada.

---

## [v0.9.0] — Marzo 2026
- `SQLiteLifeManager` CRUD + FastAPI 14 endpoints.

---

## [v0.1–0.8] — Febrero–Marzo 2026
- Arquitectura base, FastAPI REST, Bot Telegram v1–v3.

---

_Última actualización: 14 abril 2026 — 19:08 CEST_
