# 🧠 Cuaderno de Aprendizaje Python — THDORA

> **Qué es esto:**  
> Este archivo es un cuaderno vivo donde exploramos el código de THDORA archivo por archivo,
> aprendemos Python real con ejemplos de nuestro propio bot, y documentamos cada pieza
> al nivel de detalle que necesitamos para entender el proyecto completamente y poder
> hablar de él a nivel profesional (entrevistas, portfolio, colaboradores futuros).
>
> **Por qué existe:**  
> El proyecto escaló muy rápido. Sin este nivel de conocimiento del código propio,
> dependemos de la IA para entender lo que nosotros mismos escribimos — como pasó con Thea IA.
> Este documento rompe esa dependencia.
>
> **Cómo se usa:**  
> Sesión a sesión, vamos marcando ✅ los archivos explorados y añadimos notas de lo aprendido.
> Si algo no se entiende bien, se anota con ❓ para revisarlo.

---

## 📊 Estado general

| Capa | Archivos totales | Explorados | % |  
|------|-----------------|------------|---|
| 🤖 Bot — Entrypoint | 1 | 1 | 100% |
| 🤖 Bot — Handlers | 16 | 0 | 0% |
| 🤖 Bot — Utilidades | 4 | 0 | 0% |
| ⚙️ Configuración | 1 | 0 | 0% |
| 🌐 API FastAPI | ? | 0 | 0% |
| 🧪 Tests | ? | 0 | 0% |
| 🐳 Infraestructura | ? | 0 | 0% |

---

## 🗺️ Conceptos Python que iremos viendo

A medida que exploramos archivos, marcamos los conceptos que aparecen y los entendemos.

### Fundamentos
- [ ] Variables y tipos básicos (`str`, `int`, `bool`, `None`)
- [ ] Listas (`[]`) y diccionarios (`{}`)
- [ ] Funciones (`def`) — parámetros y valores de retorno
- [ ] Condicionales (`if / elif / else`)
- [ ] Bucles (`for`, `while`)
- [ ] `try / except` — gestión de errores
- [ ] f-strings — texto con variables incrustadas

### Intermedio
- [ ] `async / await` — programación asíncrona
- [ ] Clases (`class`) y métodos
- [ ] Type hints (`: str`, `-> None`, `Optional[...]`)
- [ ] Decoradores (`@property`, `@staticmethod`)
- [ ] List comprehensions (`[x for x in lista if condición]`)
- [ ] Context managers (`with ...`)
- [ ] `*args` y `**kwargs`

### Avanzado / Librerías
- [ ] `pydantic` — validación de datos y settings
- [ ] `httpx` — cliente HTTP asíncrono
- [ ] `sqlalchemy` — ORM para base de datos
- [ ] `fastapi` — framework de la API REST
- [ ] `python-telegram-bot` — framework del bot
- [ ] `langgraph` — agente IA con memoria
- [ ] `apscheduler` — tareas programadas

---

## 📁 Checklist de exploración — archivo por archivo

Marcamos cada archivo cuando: (1) lo hemos leído, (2) entendemos qué hace, (3) tiene comentarios/docstrings adecuados.

---

### 🤖 Capa 1 — Entrypoint del Bot

#### `src/bot/main.py` ✅ EXPLORADO
- **Qué hace:** Director de orquesta. Arranca el bot, registra todos los handlers, conecta con la API, el scheduler y el agente IA.
- **Funciones clave:**
  - `_check_api()` → comprueba que la API responde antes de arrancar (3 reintentos con backoff exponencial)
  - `_post_init()` → arranca APScheduler y pre-compila el grafo LangGraph
  - `_post_shutdown()` → cierra el cliente HTTP limpiamente
  - `build_app()` → construye el `Application` de Telegram con todos los handlers registrados
  - `_route_free_text()` → decide si un texto libre va a hábitos o a NLP/IA
  - `main()` → punto de entrada real: llama a `_check_api`, `build_app` y `run_polling`
- **Conceptos Python aprendidos aquí:**
  - `async def` / `await` — funciones asíncronas
  - `for ... in range(1, 4)` — bucle con 3 iteraciones
  - `try / except Exception as exc` — captura de errores
  - `2 ** attempt` — potencia (backoff exponencial)
  - `asyncio.sleep()` — espera sin bloquear
  - `context.user_data.get("clave")` — leer del cuaderno del usuario
  - Method chaining: `.token().persistence().build()`
  - `r"^patron_"` — expresiones regulares para callbacks
- **Documentación:** ✅ Suficiente para el nivel actual
- **Notas/Dudas:** ❓ ¿Cómo funciona exactamente `PicklePersistence`? ¿Qué guarda exactamente?

---

### 🤖 Capa 2 — Handlers del Bot

Orden recomendado: de menos a más complejo.

#### `src/bot/handlers/menu.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_
- **Funciones clave:** `cmd_start`, `cb_menu_home`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/common.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_
- **Funciones clave:** `cmd_cancelar`, `cb_cancel_action`, `cmd_resumen`, `error_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/diario.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Handler del comando `/diario`
- **Funciones clave:** `diario_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/stats.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Handler del comando `/stats`
- **Funciones clave:** `stats_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/voice.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Transcripción de notas de voz
- **Funciones clave:** `voice_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/weather.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Handler del comando `/tiempo`
- **Funciones clave:** `weather_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/onboarding.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Primera vez que el usuario usa el bot
- **Funciones clave:** `get_onboarding_handler`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/semana.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Vista semanal de citas y hábitos
- **Funciones clave:** `cmd_semana`, `cb_semana_nav`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/semana_nav.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Navegación paginada entre semanas
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/nlp.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Interpreta texto libre del usuario con IA (Groq/LangGraph)
- **Funciones clave:** `nlp_handler`
- **Conceptos Python:** _por descubrir_ — aquí veremos cómo se llama a la IA
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/nlp_disambig.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Cuando la IA no entiende bien, pide confirmación al usuario
- **Funciones clave:** `cb_nlp_disambig`
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/citas_slots.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Lógica de franjas horarias para citas
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/semana.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_
- **Notas/Dudas:**

#### `src/bot/handlers/habitos.py` ⬜ PENDIENTE (grande: 21KB)
- **Qué hace:** _por explorar_ — Todo el flujo de `/habitos`: crear, editar, registrar valor, borrar
- **Funciones clave:** `build_habito_handler`, `build_edit_hab_handler`, `cmd_habitos`, `cb_hab_delete`, `cb_hab_add`, `cb_hab_add_value`
- **Conceptos Python:** _por descubrir_ — aquí veremos `ConversationHandler` completo
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/citas.py` ⬜ PENDIENTE (grande: 31KB)
- **Qué hace:** _por explorar_ — Todo el flujo de `/citas`: crear, editar, ver detalle, borrar, conflictos
- **Funciones clave:** `build_nueva_handler`, `build_edit_apt_handler`, `cmd_citas`, `cb_cita_detail`, `cb_apt_delete`
- **Conceptos Python:** _por descubrir_ — el más completo del bot
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/config.py` ⬜ PENDIENTE (grande: 16KB)
- **Qué hace:** _por explorar_ — Configuración del usuario: hábitos configurables, notificaciones
- **Funciones clave:** `build_config_handler`, toggles de notificación
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/handlers/__init__.py` ✅ REVISADO
- **Qué hace:** Exporta todo lo necesario para `main.py`. Punto central de importaciones del paquete `handlers`.
- **Concepto clave:** `__init__.py` convierte una carpeta en un "paquete" Python importable. Sin él, no puedes hacer `from src.bot.handlers import cmd_start`.
- **Documentación:** ✅ Bien comentado

---

### 🤖 Capa 3 — Utilidades del Bot

#### `src/bot/api_client.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Clase `ThdoraApiClient`: todos los métodos para hablar con la API REST
- **Conceptos Python:** _por descubrir_ — aquí veremos clases, `__init__`, métodos async, `httpx`
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/http_client.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Gestión del cliente HTTP compartido (singleton)
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/scheduler.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — APScheduler para notificaciones programadas
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/utils/accum.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Acumulador de valores para el registro de hábitos
- **Conceptos Python:** _por descubrir_
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

#### `src/bot/utils/dates.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Utilidades de fechas (parseo, formato, comparación)
- **Conceptos Python:** _por descubrir_ — veremos `datetime`, `timedelta`
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:**

---

### ⚙️ Capa 4 — Configuración y Dominio

#### `src/config.py` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Lee todas las variables de entorno del `.env` con Pydantic Settings
- **Conceptos Python:** _por descubrir_ — `class Settings(BaseSettings)`, variables de entorno
- **Documentación:** ❓ por evaluar
- **Notas/Dudas:** ❓ ¿Qué pasa si falta una variable obligatoria?

---

### 🌐 Capa 5 — API FastAPI

> _Por mapear: necesitamos listar los archivos de `src/api/` primero_

#### `src/api/` ⬜ PENDIENTE — mapear estructura
- **Qué buscaremos:** routers, modelos, endpoints, middleware
- **Conceptos Python:** `@app.get(...)`, `@app.post(...)`, `Depends(...)`, schemas Pydantic

---

### 🧠 Capa 6 — Agente IA (LangGraph)

> _Por mapear: necesitamos listar los archivos de `src/agents/` primero_

#### `src/agents/` ⬜ PENDIENTE — mapear estructura
- **Qué buscaremos:** grafo LangGraph, nodos, memoria persistente, scheduler de memoria

---

### 🧪 Capa 7 — Tests

> _Por mapear: estructura en `tests/`_

#### `tests/` ⬜ PENDIENTE — mapear estructura
- **Qué buscaremos:** `conftest.py`, fixtures, mocks, cómo se testa código async
- **Conceptos Python:** `pytest`, `@pytest.fixture`, `AsyncMock`, `patch`

---

### 🐳 Capa 8 — Infraestructura

#### `Dockerfile` ✅ REVISADO
- **Qué hace:** Build multi-stage del contenedor (builder + runtime, usuario no-root)
- **Concepto clave:** Multi-stage separa el entorno de compilación del de ejecución → imagen final más pequeña y segura

#### `docker-compose.yml` ✅ REVISADO
- **Qué hace:** Orquesta todos los servicios: API, bot, Prometheus, Grafana
- **Concepto clave:** `depends_on`, `volumes`, `networks`, `environment`

#### `docker/entrypoint.sh` ✅ REVISADO
- **Qué hace:** Script de arranque — aplica migraciones Alembic y lanza el servicio correcto
- **Concepto clave:** `$SERVICE_TARGET` como variable de entorno para diferenciar api/bot en el mismo contenedor

#### `.github/workflows/ci.yml` ⬜ PENDIENTE
- **Qué hace:** _por explorar_ — Pipeline CI que corre tests en cada push
- **Concepto clave:** GitHub Actions, YAML de CI/CD

---

## 📝 Glosario Python — términos que vamos aprendiendo

| Término | Qué es | Dónde lo vimos |
|---------|--------|----------------|
| `async def` | Función asíncrona — puede pausar y dejar que otras cosas corran | `main.py` |
| `await` | "Espera esto, pero sin bloquear" | `main.py` |
| `try / except` | Captura errores para no crashear | `main.py` |
| `for x in range(n)` | Bucle que repite n veces | `main.py` |
| `2 ** n` | Potencia — 2 al cuadrado | `main.py` |
| `dict.get("clave")` | Leer del diccionario sin crashear si no existe | `main.py` |
| `__init__.py` | Convierte una carpeta en paquete importable | `handlers/__init__.py` |
| `from X import Y` | Traer una función/clase de otro archivo | en todos |
| `r"^patron"` | Expresión regular — patrón de texto | `main.py` |
| `-> None` | Type hint: esta función no devuelve nada | `main.py` |

---

## 🚦 Sesiones de exploración

### Sesión 1 — 2026-06-20
- ✅ Explorado `src/bot/main.py` al completo
- ✅ Explorado `src/bot/handlers/__init__.py`
- ✅ Auditados y corregidos: Dockerfile, docker-compose, entrypoint, requirements, .env.example, prometheus.yml
- 🎯 Próximo: `src/bot/handlers/menu.py` → primer handler real

---

## 💡 Frases para entrevistas (ir completando)

> _Aquí iremos anotando cómo explicar el proyecto en una entrevista de trabajo, con vocabulario técnico correcto._

- "THDORA es un bot de Telegram personal construido con python-telegram-bot v21, con arquitectura de microservicios: el bot consume una API REST interna hecha con FastAPI."
- "El bot usa programación asíncrona con asyncio para poder atender múltiples eventos de Telegram sin bloquearse."
- "La persistencia de estado de las conversaciones se gestiona con `PicklePersistence`, que serializa el `user_data` de cada usuario en disco."
- "Usamos LangGraph para el agente de IA con memoria persistente entre sesiones, que interpreta lenguaje natural y crea citas o registra hábitos automáticamente."
- _(añadir más a medida que exploramos el código)_
