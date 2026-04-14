# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.14.0] — 14 abril 2026

### ✨ Añadido — Modo Toki: contexto real + menú en intent desconocido

#### Diseño
La IA ya no actúa de forma autónoma cuando no entiende un mensaje.
En su lugar devuelve siempre la interfaz del bot (botones + menú), como hace Toki.
Además, para intents `consulta` y `chat`, el modelo recibe los datos reales
de la agenda antes de responder, no inventa ni dice que no tiene información.

#### `src/bot/groq_router.py`
- `route()` acepta nuevo parámetro `api_context: Optional[Dict]`
  con citas de hoy, citas de mañana y hábitos del día.
- `_build_chat_system(api_context)` — construye el system prompt
  inyectando el contexto real. Si la API falla, usa el prompt base
  (degradación elegante, el bot sigue funcionando).
- `chat_response()` recibe `api_context` y lo pasa a `_build_chat_system`.
- Intent `desconocido` → `show_menu=True` en el resultado.
  El handler es responsable de mostrar el menú, el router no genera texto.
- Docstring del módulo actualizado con sección "Contexto real (modo Toki)".

#### `src/bot/handlers/nlp.py`
- `_get_api_context(today, tomorrow)` — función nueva que hace 3 llamadas
  en paralelo con `asyncio.gather`:
  - `get_appointments(today)` — citas de hoy
  - `get_appointments(tomorrow)` — citas de mañana
  - `get_habits(today)` — hábitos de hoy
  Cada llamada está envuelta en `_safe()` — si falla no rompe el bot.
- `nlp_handler()` llama a `_get_api_context()` antes de llamar a `route()`
  y pasa el resultado como `api_context`.
- Intent `desconocido` → muestra `_MSG_MENU` + teclado `_kb_start()`.
  Ya NO responde con texto suelto genérico.
- Docstring del módulo actualizado con sección "Diseño Toki".

### 📦 Archivos modificados
| Archivo | Cambio principal |
|---|---|
| `src/bot/groq_router.py` | `api_context` + `_build_chat_system` + `show_menu` |
| `src/bot/handlers/nlp.py` | `_get_api_context` paralelo + menú en desconocido |
| `CHANGELOG.md` | Esta entrada |

### ⚠️ Nota de despliegue
No requiere cambios en `.env` ni en dependencias. Pull + reiniciar bot.

---

## [v0.13.0] — 14 abril 2026

### ✨ Añadido / Mejorado — UX, Persistencia y Personalidad (Auditoría abr-2026)

#### 1. `src/bot/handlers/nlp.py` — Indicador visual y fix hora 00:00
- **`⏳ Procesando...`**: se envía un mensaje temporal mientras Groq trabaja
  y se borra automáticamente al recibir la respuesta.
- **Fix hora 00:00**: si Groq no detecta la hora y devuelve `"00:00"`, ahora
  se pide confirmación al usuario en lugar de crear una cita a medianoche.

#### 2. `src/bot/handlers/menu.py` — /start explica los dos modos
- El mensaje de bienvenida incluye `_AYUDA_NLP` con ejemplos de lenguaje natural.

#### 3. `src/bot/main.py` — PicklePersistence (v4.0 → v4.1)
- `PicklePersistence` activa → `nlp_history` sobrevive reinicios.

#### 4. `src/bot/groq_router.py` — Personalidad THDORA refinada
- `_CHAT_SYSTEM` reescrito: 2 frases máx, sin florituras, no inventa datos.

---

## [v0.12.0] — 14 abril 2026

### ✨ Añadido — NLP con Groq (F13-base)
- `groq_router.py` completo: clasificador + extractor citas/hábitos + chat
- `handlers/nlp.py` con detección de conflicto de hora
- `docs/NLP_ARQUITECTURA.md` creado

---

## [v0.11.0] — 13 abril 2026
- `UserConfig` en SQLite, APScheduler, `/config` con notificaciones

---

## [v0.10.0] — Abril 2026
- Bot v4 modular + UX avanzada

---

## [v0.9.0] — Marzo 2026
- `SQLiteLifeManager` CRUD + FastAPI 14 endpoints

---

## [v0.1–0.8] — Febrero–Marzo 2026
- Arquitectura base, FastAPI REST, Bot Telegram v1–v3

---

_Última actualización: 14 abril 2026 — 15:51 CEST_
