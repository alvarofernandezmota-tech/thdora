# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.15.0] — 14 abril 2026

### ✨ Mejoras de calidad — Solapamiento real, horario visual, rendimiento y tests

#### Contexto
Sesión de mejora transversal: se detectaron y corrigieron 3 problemas de lógica y rendimiento
que afectaban a la fiabilidad del sistema, y se añadió cobertura de tests para las funciones críticas.

---

#### 1. `src/api/routers/appointments.py` — Conflicto con solapamiento real

**Problema anterior:** `check_conflict` comparaba únicamente hora exacta (`apt["time"] == time_str`).
Una cita a las 17:00 no bloqueaba el slot de las 17:30, permitiendo doble reserva.

**Solución:** Solapamiento real con duración predeterminada de 60 minutos.

- `_DEFAULT_DURATION_MIN = 60` — constante de duración predeterminada.
- `_time_to_minutes(time_str)` — convierte `'HH:MM'` a minutos desde medianoche.
- `_find_overlap(apts, new_time, duration)` — detecta solapamiento con la fórmula:
  ```
  new_start < exist_end  AND  new_end > exist_start
  ```
  Cubre todos los casos: hora exacta, inicio dentro del bloque, nueva tapa inicio de otra.
- `check_conflict` ahora acepta `?duration=` como query param (rango 1–480 min)
  para soportar citas de duración variable en el futuro.
- Docstring actualizado con descripción del endpoint v2.2.

---

#### 2. `src/bot/handlers/nlp.py` — Horario visual con bloques de duración real

**Problema anterior:** `_build_day_schedule` no existía en la forma correcta;
la detección de conflicto no mostraba el rango de la cita existente.

**Solución:** Horario visual por franjas de 30 min con bloques de duración completa.

- `_build_day_schedule(citas, date_str, highlight_time, duration)` — genera franjas
  de 30 min entre 08:00 y 22:00. Cada cita ocupa su slot de inicio más los siguientes
  hasta completar 60 min. Emojis: 🔴 ocupado | 🟢 libre | ⚠️ slot del conflicto solicitado.
- El nombre de la cita aparece solo en el primer slot; los de continuación muestran `┃`.
- `_end_time(start, duration)` — calcula la hora de fin para mostrarla en el mensaje
  de conflicto: `⚠️ Las 17:30 solapan con *Dentista* (17:00–18:00)`.
- `_time_to_min(t)` — helper local de conversión.

---

#### 3. `src/bot/handlers/semana.py` — De 14 llamadas HTTP a 2 concurrentes

**Problema anterior:** `_show_semana` hacía 7 llamadas a `get_appointments` + 7 a `get_habits`
en serie — ~14 round-trips para renderizar la vista semanal.

**Solución:** `asyncio.gather` + endpoint de semana existente.

- `asyncio.gather(get_appointments_week, _get_week_habits)` — ambas peticiones
  se lanzan en paralelo. Dentro de `_get_week_habits`, los 7 días también van en paralelo.
- `_safe_week_apts(monday_str)` — wrapper con manejo de error sobre `get_appointments_week`.
- `_get_week_habits(monday)` — lanza 7 `get_habits` con `asyncio.gather`, cada uno
  envuelto en `_safe_habits` para degradación elegante.
- Constantes extraidas: `_DAY_NAMES`, `_MONTHS`.
- **Resultado:** de ~14 round-trips en serie a 2 concurrentes (Ô7 más rápido en condiciones normales).

---

#### 4. `tests/unit/test_appointments_overlap.py` — 18 tests nuevos

Cobertura completa de `_find_overlap` y `_time_to_minutes`:

| Clase | Tests | Qué cubre |
|---|---|---|
| `TestTimeToMinutes` | 5 | Medianoche, hora exacta, minutos, cero izquierda |
| `TestFindOverlap` | 13 | Día vacío, hora libre, contigua antes/después, hora exacta, inicio dentro, nueva tapa inicio, duración personalizada |

No requieren API ni base de datos. Corren con `pytest tests/unit/ -v`.

---

#### 5. `tests/unit/bot/test_nlp_schedule.py` — 14 tests nuevos

Cobertura de `_build_day_schedule`, `_end_time` y `_time_to_min`:

| Clase | Tests | Qué cubre |
|---|---|---|
| `TestTimeToMin` | 3 | Conversiones básicas |
| `TestEndTime` | 4 | Suma 60 min, cruza hora, duración personalizada, cero izquierda |
| `TestBuildDaySchedule` | 7 | Día vacío, límites 08–22, cita ocupa 2 slots, nombre solo en 1er slot, highlight en ocupado y libre, dos citas sin mezcla |

---

#### 6. `README.md` — Portfolio-ready

- Badges de CI, Python, FastAPI y License en la cabecera.
- Tabla de stack técnico con justificación de cada decisión.
- Diagrama ASCII de arquitectura (Usuario → Bot → API → SQLite).
- Sección "Decisiones de diseño destacadas" con las 4 decisiones clave del proyecto.
- Estructura de tests actualizada con los ficheros nuevos.
- Sección de texto libre con ejemplos de uso natural.

---

### 📦 Archivos modificados

| Archivo | Tipo de cambio |
|---|---|
| `src/api/routers/appointments.py` | 🔧 Fix + mejora (solapamiento real) |
| `src/bot/handlers/nlp.py` | 🔧 Fix + mejora (horario visual) |
| `src/bot/handlers/semana.py` | ⚡ Optimización rendimiento |
| `tests/unit/test_appointments_overlap.py` | ✨ Nuevo |
| `tests/unit/bot/__init__.py` | ✨ Nuevo |
| `tests/unit/bot/test_nlp_schedule.py` | ✨ Nuevo |
| `README.md` | 📝 Documentación |
| `CHANGELOG.md` | 📝 Esta entrada |

### ⚠️ Nota de despliegue
No requiere cambios en `.env` ni en dependencias. `git pull` + reiniciar API y bot.

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

_Última actualización: 14 abril 2026 — 18:21 CEST_
