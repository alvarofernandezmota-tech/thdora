# 🏗️ THDORA — Arquitectura y módulos

> Documentación técnica completa: qué hace cada fichero, por qué existe y cómo se relaciona con el resto.
>
> **Navegación:** [README](../README.md) · [ROADMAP](../ROADMAP.md) · [CHANGELOG](../CHANGELOG.md) · [INDEX](INDEX.md)

---

## Visión general del sistema

THDORA tiene **tres capas independientes** que se comunican entre sí pero no dependen unas de otras directamente:

```
┌──────────────────────────────────────────┐
│  BOT TELEGRAM                           │
│  python-telegram-bot v22               │
│  ConversationHandlers + inline buttons │
└───────────────┬───────────────────────┘
               │ HTTP (httpx async)
               │ ThdoraApiClient
┌───────────────┬───────────────────────┐
│  API REST                              │
│  FastAPI + Pydantic                    │
│  14 endpoints CRUD + semana + stats    │
└───────────────┬───────────────────────┘
               │ SQLAlchemy ORM
               │ SQLiteLifeManager
┌───────────────┬───────────────────────┐
│  PERSISTENCIA                          │
│  SQLite (data/thdora.db)               │
│  Tablas: appointments, habits          │
└──────────────────────────────────────────┘
```

**Por qué este diseño:** el bot no accede nunca a la base de datos directamente. Solo habla con la API. Esto permite en el futuro cambiar el almacenamiento (PostgreSQL, cloud) sin tocar nada del bot.

---

## 📚 Módulo `src/core/` — Abstracción de negocio

### ¿Para qué sirve?
Define el **contrato** de lo que el sistema puede hacer, independientemente de cómo se almacenen los datos. Es el corazón del proyecto.

### Ficheros

#### `src/core/abstract_life_manager.py`
- **Qué es:** clase abstracta base con métodos abstractos para citas y hábitos
- **Por qué existe:** permite tener múltiples implementaciones (memoria, JSON, SQLite, cloud) sin cambiar la API ni el bot
- **Patrón:** Strategy / Repository

#### `src/core/impl/sqlite_lifemanager.py`
- **Qué es:** implementación activa que usa SQLite como backend
- **Por qué existe:** es el único `LifeManager` en uso en producción
- **Hace:** CRUD completo de citas y hábitos sobre la base de datos real
- **No hace:** validaciones de negocio (esas van en la API)

---

## 📚 Módulo `src/db/` — Base de datos

### ¿Para qué sirve?
Todo lo relacionado con SQLite: conexión, modelos ORM y ciclo de vida de las sesiones.

### Ficheros

#### `src/db/base.py`
- **Qué es:** configura el engine SQLAlchemy, la sesión y `Base` declarativa
- **Exports clave:** `get_session()`, `init_db()`, `Base`
- **Por qué existe:** centraliza la conexión. Si cambia la DB (SQLite → PostgreSQL) solo se toca este fichero

#### `src/db/models.py`
- **Qué es:** define las tablas como clases Python con SQLAlchemy ORM
- **Tablas:**
  - `Appointment` — campos: `date`, `time`, `name`, `type`, `notes`, `index`
  - `Habit` — campos: `date`, `name`, `value`
- **Método `to_dict()`** en cada modelo: convierte la fila a diccionario para la API

---

## 📚 Módulo `src/api/` — API REST

### ¿Para qué sirve?
Expone todos los datos y operaciones a través de HTTP. El bot y cualquier cliente externo se comunican exclusivamente por aquí.

### Ficheros

#### `src/api/main.py`
- **Qué es:** entrypoint de FastAPI. Registra todos los routers y el health check
- **Arranca con:** `uvicorn src.api.main:app --reload --port 8000`
- **Endpoint especial:** `GET /health` → `{"status": "ok"}` — usado por el bot al arrancar para saber si la API está lista

#### `src/api/deps.py`
- **Qué es:** inyección de dependencias de FastAPI
- **Hace:** provee una instancia singleton de `SQLiteLifeManager` a todos los routers
- **Por qué existe:** evita crear una nueva conexión a DB en cada request

#### `src/api/routers/appointments.py`
- **Qué es:** todos los endpoints de citas
- **Endpoints:** `POST`, `GET`, `PUT`, `DELETE` + semana + rango + upcoming
- **Detalle importante:** el `index` de una cita es su posición en la lista del día (0, 1, 2…), no un ID global

#### `src/api/routers/habits.py`
- **Qué es:** todos los endpoints de hábitos
- **Endpoints:** `POST` (upsert), `GET`, `PUT`, `DELETE` + semana + rango + stats
- **Detalle importante:** `POST /habits/{date}` hace upsert — si el hábito ya existe lo actualiza, si no lo crea

#### `src/api/routers/summary.py`
- **Qué es:** endpoints de resumen diario y semanal
- **Hace:** agrega citas + hábitos del día/semana en una sola respuesta

---

## 📚 Módulo `src/bot/` — Bot Telegram

### ¿Para qué sirve?
Toda la interfaz de usuario del sistema. El usuario solo ve el bot; nunca interactúa con la API directamente.

### Ficheros raíz del bot

#### `src/bot/main.py`
- **Qué es:** entrypoint del bot. Registra todos los handlers en orden de prioridad
- **Orden de registro (crítico):**
  1. `ConversationHandler`s (máxima prioridad — capturan primero)
  2. `CallbackQueryHandler`s globales
  3. `MessageHandler` texto libre
  4. `CommandHandler`s simples
  5. `error_handler`
- **Por qué importa el orden:** si un `CallbackQueryHandler` global está registrado antes que un `ConversationHandler`, captura los callbacks y el flujo de conversación nunca avanza

#### `src/bot/api_client.py`
- **Qué es:** cliente HTTP asíncrono que encapsula todas las llamadas a la API REST
- **Librería:** `httpx` (asíncrono, compatible con `asyncio`)
- **Por qué existe:** el bot nunca llama a la DB directamente. Todo pasa por este cliente. Si cambia la URL de la API, solo se cambia aquí
- **Métodos principales:**
  ```
  get_appointments(date)          → GET /appointments/{date}
  create_appointment(...)         → POST /appointments/{date}
  update_appointment(...)         → PUT /appointments/{date}/{index}
  delete_appointment(date, index) → DELETE /appointments/{date}/{index}
  get_habits(date)                → GET /habits/{date}
  log_habit(date, name, value)    → POST /habits/{date}
  update_habit(...)               → PUT /habits/{date}/{habit}
  delete_habit(date, habit)       → DELETE /habits/{date}/{habit}
  health()                        → GET /health
  ```

#### `src/bot/keyboards.py`
- **Qué es:** todas las funciones que construyen teclados inline de Telegram
- **Por qué existe:** separa la UI del comportamiento. Los handlers no construyen keyboards directamente
- **Funciones clave:**
  ```
  _kb_start()           → menú principal (/start)
  _kb_franjas()         → [🌅 Mañana][🌆 Tarde][🌙 Noche][✏️ Exacta]
  _kb_horas_franja(key) → 8 botones de hora para la franja seleccionada
  _kb_cuartos(hora)     → [HH:00][HH:15][HH:30][HH:45][✏️ Exacta]
  _kb_tipos()           → [Médica][Personal][Trabajo][Otra]
  _nav_keyboard(date, vista) → [◀️][Fecha][▶️] + botones de cambio de vista
  _kb_back(date, vista) → [← Volver]
  _kb_cita_detail(...)  → [Editar][Borrar][← Volver]
  _kb_hab_actions(...)  → [✏️ Editar][🗑️ Borrar][➕ Sumar]
  _kb_hab_value(cfg)    → botones rápidos si hay config de hábito
  ```

### `src/bot/utils/`

#### `src/bot/utils/dates.py`
- **Qué es:** helpers de fechas para el bot
- **Por qué existe:** la fecha llega como texto libre del usuario (`hoy`, `mañana`, `27/03`…) y hay que normalizar siempre al formato `YYYY-MM-DD` que usa la API
- **Funciones:**
  ```
  _parse_date_flex(text) → "2026-04-13" (desde texto libre del usuario)
  _parse_date_arg(arg)   → "2026-04-13" (desde argumento de comando)
  _date_label(date_str)  → "lunes 13 de abril" (para mostrar al usuario)
  _date_short(date_str)  → "lun 13 abr" (para botones compactos)
  _greeting()            → "Buenos días" / "Buenas tardes" / "Buenas noches"
  _monday(date_str)      → lunes de la semana de esa fecha
  ```

#### `src/bot/utils/accum.py`
- **Qué es:** lógica de acumulación de valores de hábitos
- **Por qué existe:** los hábitos pueden sumarse (`+2`), sobreescribirse (`8h`) o acumularse con unidades (`+30min`)
- **Funciones:**
  ```
  _accumulate_value(existing, new_input) → valor final
    Ejemplos:
      ("6h", "+2h")   → "8h"
      ("1.5L", "+0.5L") → "2.0L"
      (None, "+3")    → "3"
      ("5", "8")      → "8"  (sobreescribe)
  _clean_acum_context(context) → limpia user_data de acumulación
  ```

### `src/bot/handlers/`

#### `src/bot/handlers/__init__.py`
- **Qué es:** re-exporta todo lo que necesita `main.py`
- **Por qué existe:** `main.py` hace un solo import limpio de aquí. Si se refactorizan los módulos internos, `main.py` no cambia

#### `src/bot/handlers/menu.py`
- **Qué es:** handler del menú principal
- **Handlers:**
  - `cmd_start` → responde a `/start`, muestra menú con saludo + citas de hoy
  - `cb_menu_home` → responde al callback `menu_home` (botón 🏠 Menú desde cualquier vista)
  - `cb_quick_config` → responde al botón ⚙️ Config del menú
- **Importante:** los botones `➕ Nueva cita` y `➕ Nuevo hábito` del menú **no** pasan por aquí — los capturan directamente los `ConversationHandler` de `citas.py` y `habitos.py`

#### `src/bot/handlers/citas.py`
- **Qué es:** todo lo relacionado con citas
- **ConversationHandlers:**
  - `build_nueva_handler()` → flujo de creación de cita con franjas horarias
    - Entry points: `/nueva` (comando) + `quick_nueva_*` (botón menú)
    - Estados: `NUEVA_DATE` → `NUEVA_FRANJA` → `NUEVA_HORA_PUNTO` → `NUEVA_HORA_CUARTO` → `NUEVA_TIME` → `NUEVA_CONFLICT` → `NUEVA_NOMBRE` → `NUEVA_TYPE` → `NUEVA_NOTES`
  - `build_edit_apt_handler()` → flujo de edición
    - Entry point: callback `ae_{date}_{index}` (botón ✏️ en la lista de citas)
- **Callbacks sueltos:**
  - `cb_citas_nav` → navegación ◀️▶️ entre días
  - `cb_cita_detail` → vista detalle al pulsar en la hora de una cita
  - `cb_apt_delete` / `cb_apt_delete_confirm` → borrar con confirmación

#### `src/bot/handlers/habitos.py`
- **Qué es:** todo lo relacionado con hábitos
- **ConversationHandlers:**
  - `build_habito_handler()` → flujo de registro de hábito
    - Entry points: `/habito` (comando) + `quick_habito_*` (botón menú)
    - Estados: `HABITO_NOMBRE` → `HABITO_VALUE` → `HABITO_CONFLICT`
  - `build_edit_hab_handler()` → flujo de edición
    - Entry point: callback `he_{date}_{habit}`
- **Callbacks sueltos:**
  - `cb_habitos_nav` → navegación entre días
  - `cb_hab_delete` / `cb_hab_delete_confirm` → borrar con confirmación
  - `cb_hab_add` → acumulación rápida desde lista de hábitos
  - `cb_hab_add_value` → recibe el valor a acumular (texto libre)

#### `src/bot/handlers/semana.py`
- **Qué es:** vista semanal
- **Handlers:**
  - `cmd_semana` → muestra la semana actual con citas + hábitos por día
  - `cb_semana_nav` → navegar entre semanas con ◀️▶️

#### `src/bot/handlers/config.py`
- **Qué es:** configuración de tipos de hábitos
- **ConversationHandler:** `build_config_handler()`
  - Entry point: `/config`
  - Estados: `CFG_NOMBRE` → `CFG_TYPE` → `CFG_UNIT` → `CFG_QUICK`
  - Permite definir si un hábito es numérico, tiempo, sí/no o texto libre
  - Define botones rápidos de valores (ej: `6h,7h,8h` para sueño)

#### `src/bot/handlers/common.py`
- **Qué es:** handlers genéricos compartidos
- **Handlers:**
  - `cmd_cancelar` → cancela cualquier flujo activo
  - `cb_cancel_action` → versión inline del cancelar
  - `cmd_resumen` → resumen del día (citas + hábitos)
  - `error_handler` → captura excepciones no controladas y las loggea sin crashear el bot

---

## 📚 Ficheros raíz del proyecto

#### `pyproject.toml`
- **Qué es:** configuración del proyecto Python (PEP 517/518)
- **Hace:** define dependencias, scripts, versión, metadatos, config de pytest y linters
- **Por qué `pyproject.toml` y no `setup.py`:** es el estándar moderno de Python desde 2021

#### `Makefile`
- **Qué es:** atajos de comandos frecuentes
- **Comandos principales:**
  ```
  make dev          → instala dependencias en modo desarrollo
  make run-api      → arranca FastAPI con hot reload
  make run-bot      → arranca el bot
  make test         → ejecuta todos los tests
  make test-bot     → solo tests del bot
  make test-cov     → tests con cobertura
  make docker-build → construye imagen Docker
  make docker-up    → arranca api + bot en contenedores
  make docker-down  → para los contenedores
  make docker-logs  → logs en vivo
  make docker-db    → consola SQLite del contenedor
  make lint         → ruff + mypy
  make fmt          → black + isort
  ```

#### `Dockerfile`
- **Qué es:** imagen Docker del proyecto
- **Base:** Python 3.12 slim
- **Hace:** instala deps, copia código, expone puerto 8000
- **Nota:** API y bot usan la misma imagen — el comando de inicio varía en `docker-compose.yml`

#### `docker-compose.yml`
- **Qué es:** orquestación de servicios
- **Servicios:**
  - `api` → FastAPI en puerto 8000, con volumen `data/` para la DB
  - `bot` → Bot Telegram, depende de `api`, usa el mismo volumen
- **Por qué volumen compartido:** bot y API necesitan acceder a `thdora.db`, aunque en producción el bot nunca toca la DB directamente (solo habla con la API)

#### `.env.example`
- **Qué es:** plantilla de variables de entorno
- **Variables:**
  ```
  TELEGRAM_BOT_TOKEN=    ← obligatorio (de @BotFather)
  THDORA_API_URL=http://localhost:8000
  THDORA_DB_PATH=data/thdora.db
  ```

---

## 📚 Tests

#### `tests/unit/bot/test_dates.py`
- Prueba `_parse_date_flex`: `hoy`, `mañana`, `27/03`, `lunes`…
- Prueba `_date_label`, `_date_short`, `_greeting`, `_monday`

#### `tests/unit/bot/test_accum.py`
- Prueba `_accumulate_value` con sumas, unidades, sobreescrituras y edge cases

#### `tests/unit/bot/test_keyboards.py`
- Prueba que los teclados generan el número correcto de botones
- Verifica callback_data de cada botón

#### `tests/bot/test_handlers_citas.py`
- Prueba los handlers de citas con mocks de Telegram y la API
- Verifica transiciones de estado en `ConversationHandler`

#### `tests/bot/test_handlers_habitos.py`
- Prueba los handlers de hábitos con mocks
- Verifica acumulación y conflictos

---

## 📚 Decisiones de diseño relevantes

### ¿Por qué FastAPI y no Django?
THDORA es una API ligera y asíncrona. FastAPI es idóneo: tipado con Pydantic, documentación automática en `/docs`, nativo async, y 10x menos boilerplate que Django REST.

### ¿Por qué `python-telegram-bot` v22 y no Aiogram?
`python-telegram-bot` tiene mejor soporte de `ConversationHandler` con estados complejos, que es exactamente lo que necesita THDORA para los flujos de creación de citas y hábitos.

### ¿Por qué SQLite y no PostgreSQL?
En esta fase, THDORA es mono-usuario y corre en local o en un VPS pequeño. SQLite es suficiente, no necesita servidor separado y los datos persisten en un fichero. La abstracción `AbstractLifeManager` permite migrar a PostgreSQL cambiando solo `SQLiteLifeManager`.

### ¿Por qué el bot no accede a la DB directamente?
Aislamiento de responsabilidades. El bot es una interfaz de usuario, no una capa de datos. Esto permite desplegar el bot y la API en máquinas distintas, escalarlos por separado, y testearlos de forma independiente.

### ¿Por qué `ConversationHandler` con `per_message=False`?
Los flujos de THDORA son por usuario, no por mensaje. Un usuario empieza `/nueva`, escribe la fecha, la franja, la hora… todo en mensajes separados. `per_message=False` es el modo correcto para este patrón.

---

_Última actualización: 13 abril 2026 — 20:50 CEST_
