# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.13.0] — 14 abril 2026

### ✨ Añadido / Mejorado — UX, Persistencia y Personalidad (Auditoría abr-2026)

#### 1. `src/bot/handlers/nlp.py` — Indicador visual y fix hora 00:00
- **`⏳ Procesando...`**: se envía un mensaje temporal mientras Groq trabaja
  y se borra automáticamente al recibir la respuesta. El usuario ve feedback
  inmediato y no cree que el bot está caído durante el llamado LLM (~1-2s).
- **Fix hora 00:00**: si Groq no detecta la hora y devuelve `"00:00"`, ahora
  se pide confirmación al usuario en lugar de crear una cita a medianoche.
  Ref: auditoría UX-1 (hora inválida sin aviso).

#### 2. `src/bot/handlers/menu.py` — /start explica los dos modos
- El mensaje de bienvenida en `/start` y en el botón 🏠 Menú incluye ahora
  una sección `_AYUDA_NLP` que muestra dos ejemplos de uso de lenguaje natural:
  `"mañana dentista a las 5"` y `"dormí 7 horas"`.
- Antes el usuario tenía que descubrir por sí solo que podía escribir en
  lenguaje natural. Ahora se explica en la primera pantalla.
  Ref: auditoría UX-2 (onboarding incompleto).

#### 3. `src/bot/main.py` — PicklePersistence (v4.0 → v4.1)
- **`PicklePersistence`** activa con `filepath=data/bot_persistence.pkl`.
- Persiste `user_data` completo entre reinicios del proceso bot:
  - `nlp_history` (contexto conversacional de Groq)
  - `acum_hab_nombre` (flujo de acumulación de hábito en curso)
- `store_bot_data=False` y `store_chat_data=False` para mantener el pkl pequeño.
- El directorio `data/` se crea automáticamente si no existe.
- Documentación del bloque de persistencia añadida al docstring del módulo.
  Ref: auditoría UX-3 (contexto NLP se pierde en cada reinicio).

#### 4. `src/bot/groq_router.py` — Personalidad THDORA refinada
- **`_CHAT_SYSTEM`** reescrito:
  - Nombre explícito: `"Eres THDORA, asistente personal de Álvaro"`
  - Límite de 2 frases (antes 3), sin florituras ni saludos innecesarios
  - Instrucción explícita de no inventar datos de citas o hábitos
  - Ejemplos de respuesta mejorados y más naturales
- Añadido comentario en el docstring del módulo indicando que `_CHAT_SYSTEM`
  es el punto de control de la personalidad del bot y que se puede editar
  sin tocar ningún otro módulo.
  Ref: auditoría PERS-1 (personalidad sin documentar).

### 📁 Archivos modificados
| Archivo | Cambio principal |
|---|---|
| `src/bot/handlers/nlp.py` | ⏳ Procesando + fix hora 00:00 |
| `src/bot/handlers/menu.py` | /start explica lenguaje natural |
| `src/bot/main.py` | PicklePersistence activa |
| `src/bot/groq_router.py` | _CHAT_SYSTEM refinado |
| `CHANGELOG.md` | Este registro |

### ⚠️ Nota de despliegue
```
# El archivo data/bot_persistence.pkl se crea automáticamente.
# Añadir a .gitignore si aún no está:
data/bot_persistence.pkl
```

---

## [v0.12.0] — 14 abril 2026

### ✨ Añadido — NLP con Groq (F13-base)

- **`src/bot/groq_router.py`** — Orquestador NLP completo:
  - `classify_intent()` con `llama-3.1-8b-instant` (~50ms)
  - `extract_cita()` con `llama-3.3-70b-versatile` → JSON estructurado
  - `extract_habito()` con `llama-3.3-70b-versatile` → JSON estructurado
  - `chat_response()` con `llama-3.3-70b-versatile` → respuesta libre
  - `route()` — orquestador principal con historial de 10 mensajes
  - Memoria conversacional en `context.user_data["nlp_history"]`

- **`src/bot/handlers/nlp.py`** — Handler de Telegram:
  - Detecta conflictos de hora antes de crear cita
  - Formato de respuesta consistente con el resto del bot
  - Fallback a `/nueva` o `/habito` si la extracción falla

- **`src/bot/main.py`** — Actualizado:
  - `_route_free_text()` prioriza `acum_hab_nombre` y cae a NLP
  - Import de `nlp_handler`
  - Documentación de `GROQ_API_KEY` en docstring

- **`docs/NLP_ARQUITECTURA.md`** — Documentación completa:
  - Decisiones de arquitectura multi-modelo
  - Roadmap de proveedores opcionales (OpenRouter, Claude, Gemini)
  - Ejemplos de uso y plan de voz (Whisper)

### 🔧 Requiere para activar
```
GROQ_API_KEY=gsk_xxxx  ← añadir al .env
pip install groq        ← instalar dependencia
```

---

## [v0.11.0] — 13 abril 2026

### ✨ Añadido — F12 Notificaciones + Documentación técnica

- `UserConfig` en SQLite (horarios resumen + evening)
- APScheduler integrado: resumen diario + evening log + jobs one-shot por cita
- `/config` → rama notificaciones con horarios configurables
- Scheduler arranca en `post_init` (sin RuntimeError)
- Fix entry points `/config`: `quick_config` como entry_point del ConversationHandler

### 📚 Documentación
- `docs/FLUJOS_DETALLADOS.md`
- `docs/API_REFERENCE.md`
- `docs/CONVENCIONES.md`
- `docs/INDEX.md`
- `docs/F12_NOTIFICACIONES_DESIGN.md`

---

## [v0.10.0] — Abril 2026

### ✨ Añadido — Bot v4 modular + UX avanzada
- Refactor handlers en package `src/bot/handlers/`
- Franjas horarias en `/nueva`: 🌅 Mañana / 🌆 Tarde / 🌙 Noche
- Entry points desde botones del menú (➕ cita, ➕ hábito)
- Vista detalle de cita al pulsar ⏰ hora
- Editar nombre y valor de hábito inline
- Cambio vista Citas ↔ Hábitos desde la nav
- Conflicto hábito: Sobreescribir / Sumar / Cancelar

---

## [v0.9.0] — Marzo 2026

### ✨ Añadido — Persistencia SQLite
- `SQLiteLifeManager` CRUD completo
- `data/thdora.db` — datos persistentes entre reinicios
- 14 endpoints REST en FastAPI
- `GET /summary/{date}`, `/week`, `/range`, `/stats`

---

## [v0.1–0.8] — Febrero–Marzo 2026

- Arquitectura base (`AbstractLifeManager`, `MemoryLifeManager`, `JsonLifeManager`)
- FastAPI REST con CRUD citas y hábitos
- Bot Telegram v1–v3: comandos, inline buttons, fechas flexibles
- Endpoints temporales (semana, rango, próximas citas)

---

_Última actualización: 14 abril 2026 — 12:25 CEST_
