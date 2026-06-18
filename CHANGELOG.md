# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.21.3] — 18 junio 2026 (noche)

### 🐛 Fix — Arranque en máquina nueva: 4 bugs encadenados resueltos

#### Resumen de sesión
Sesión de troubleshooting al clonar el repo en una máquina nueva (`madre` / `~/Projects/thdora`)
y levantar el stack con Docker. Se resolvieron 4 bugs encadenados hasta conseguir
que el bot arrancara correctamente. Sin cambios en lógica de negocio.

---

#### Bug 1 — `ImportError: cannot import name '_invalidate_cache'`

**Síntoma:**
```
ImportError: cannot import name '_invalidate_cache' from 'src.bot.handlers.nlp'
```

**Causa raíz:** El contenedor corría una imagen desactualizada donde `nlp.py`
no tenía aún las funciones `_invalidate_cache`, `_time_to_min`, `_build_day_schedule`
que `nlp_disambig.py` esperaba.

**Fix:** `git reset --hard origin/main` + `docker compose build bot` desde la
carpeta correcta del repo.

---

#### Bug 2 — `fatal: not a git repository` + `no configuration file provided`

**Síntoma:** Todos los comandos `git` y `docker compose` fallaban desde `~`.

**Causa raíz:** El repo no estaba clonado en esa máquina. El directorio de trabajo
era `~` (home), no la carpeta del proyecto.

**Fix:**
```bash
cd ~/Projects
git clone git@github.com:alvarofernandezmota-tech/thdora.git
cd thdora
```

Regla: siempre ejecutar `git` y `docker compose` desde `~/Projects/thdora`.

---

#### Bug 3 — `.env not found`

**Síntoma:**
```
env file /home/varopc/Projects/thdora/.env not found
```

**Causa raíz:** El `.env` existía en el clone anterior (`~/dev/thdora`) pero no
en el nuevo clone (`~/Projects/thdora`). Docker busca `.env` en la misma carpeta
donde se ejecuta `docker compose`.

**Fix:**
```bash
cp ~/dev/thdora/.env ~/Projects/thdora/.env
```

---

#### Bug 4 — `ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite'`

**Síntoma:**
```
ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite'
```

**Causa raíz:** `langgraph>=0.2.0` ya no incluye el checkpointer SQLite en el
paquete principal. Desde cierta versión se separó al paquete independiente
`langgraph-checkpoint-sqlite`.

**Fix:** Añadido `langgraph-checkpoint-sqlite>=2.0.0` en `requirements.txt` y
`pyproject.toml`. Rebuild de imagen Docker.

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `requirements.txt` | ✨ `langgraph-checkpoint-sqlite>=2.0.0` |
| `pyproject.toml` | ✨ `langgraph-checkpoint-sqlite>=2.0.0` + deps LangGraph en `dependencies` |
| `docs/diario-2026-06-18.md` | 📝 Diario técnico detallado de la sesión |
| `CHANGELOG.md` | 📝 Esta entrada |

### ⚠️ Nota para arranques en máquina nueva

Siempre seguir estos pasos en orden:
```bash
git clone git@github.com:alvarofernandezmota-tech/thdora.git ~/Projects/thdora
cd ~/Projects/thdora
cp /ruta/anterior/.env .env          # o crear desde .env.example
docker compose up -d --build
docker compose logs -f bot
```

---

## [v0.21.2] — 17 junio 2026 (noche)

### 🚀 Deploy — Stack completo dockerizado: API + Bot + Prometheus + Grafana

#### Resumen de sesión
Sesión de despliegue e infraestructura. El objetivo era levantar el stack completo
(API + Bot + Prometheus + Grafana) en Docker Compose por primera vez en producción.
Se resolvieron 6 bugs de infraestructura encadenados hasta conseguir todos los
servicios `healthy` y el bot arrancando. Sin cambios en lógica de negocio.

---

#### Bug 1 — Healthcheck usaba `curl` (no disponible en imagen `python:3.12-slim`)

**Síntoma:** `OCI runtime exec failed: exec: "curl": executable file not found in $PATH`

**Fix:** Reemplazado `curl -f http://localhost:8000/` por:
```yaml
test: ["CMD", "python3", "-c", "import urllib.request..."]
```

---

#### Bug 2 — `./data/thdora.db` readonly (UID mismatch)

**Síntoma:** `sqlalchemy.exc.OperationalError: attempt to write a readonly database`

**Causa raíz:** El bind mount `./data` pertenecía a `root`, pero el contenedor
corre como `user: "1000:1000"` (usuario `thdora` creado en el Dockerfile).

**Fix permanente:**
```bash
sudo chown -R 1000:1000 ./data ./logs
```
Y en `scripts/deploy.sh` se automatiza en cada despliegue.

---

#### Bug 3 — `git pull` fallaba por cambios sin commitear en servidor

**Síntoma:** `error: cannot pull with rebase: You have unstaged changes.`

**Fix:** Sustituido `git pull` por:
```bash
git fetch --quiet origin
git reset --hard origin/main
```
Documentado en `scripts/deploy.sh` como flujo estándar de deploy.

---

#### Bug 4 — `prometheus-fastapi-instrumentator` v7 incompatible con FastAPI + sub-routers

**Síntoma:** `AttributeError: '_IncludedRouter' object has no attribute 'path'`

**Causa raíz:** `prometheus-fastapi-instrumentator>=6.1.0` instaló la v7.x que
rompió la API interna de inspección de rutas con FastAPI moderno.

**Fix:** Reemplazado el instrumentator completo por endpoint `/metrics` nativo:
```python
from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```
Además pineado en `requirements.txt`: `prometheus-fastapi-instrumentator>=6.1.0,<7.0.0`

---

#### Bug 5 — Servicio `bot` no existía en `docker-compose.yml`

**Fix:** Añadido servicio `bot` con:
- `depends_on: thdora: condition: service_healthy`
- `user: "1000:1000"`
- `THDORA_API_URL: http://thdora:8000`
- `entrypoint-bot.sh` esperando `/health/live` antes de arrancar

---

#### Bug 6 — `ImportError: cannot import name 'get_scheduler'`

**Síntoma:** `bot/main.py` importaba `get_scheduler` de `src.bot.scheduler` pero
el módulo solo tenía la clase `Scheduler` para Telegram.

**Fix:** Añadido singleton `get_scheduler()` en `scheduler.py`:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

_scheduler: AsyncIOScheduler | None = None

def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Europe/Madrid")
    return _scheduler
```

---

#### Nuevo: `scripts/deploy.sh`

Script de despliegue reproducible que automatiza:
1. `git fetch + reset --hard origin/main`
2. `mkdir -p ./data ./logs && sudo chown -R 1000:1000`
3. `docker compose down --remove-orphans`
4. `docker compose up -d --build`
5. Verificación automática de `/health/live`

```bash
bash scripts/deploy.sh           # con rebuild
bash scripts/deploy.sh --no-build  # sin rebuild
```

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `docker-compose.yml` | ✨ Servicio `bot` + `user:1000:1000` + healthcheck `/health/live` |
| `docker/entrypoint-bot.sh` | 🔧 Espera `/health/live` (no `/`) antes de arrancar bot |
| `src/api/main.py` | 🔧 Endpoint `/` devuelve 200 + integra `health_router` y `setup_prometheus` |
| `src/monitoring/metrics.py` | 🔧 `/metrics` nativo sin `prometheus-fastapi-instrumentator` |
| `src/bot/scheduler.py` | 🔧 Añadido `get_scheduler()` singleton APScheduler |
| `requirements.txt` | 🔒 `prometheus-fastapi-instrumentator>=6.1.0,<7.0.0` |
| `scripts/deploy.sh` | ✨ Script de deploy reproducible |
| `CHANGELOG.md` | 📝 Esta entrada |

### ⚠️ Nota de despliegue

Siempre usar `bash scripts/deploy.sh` — nunca `git pull` directo en servidor
(falla si hay cambios locales sin commitear).

Antes del primer arranque en servidor nuevo:
```bash
sudo chown -R 1000:1000 ./data ./logs
rm -f ./data/thdora.db   # solo si es instalación nueva
```

### ✅ Estado del stack tras esta sesión

```
thdora      ✔ healthy   — API en http://localhost:8000/docs
thdora-bot  ✔ running   — arrancando (pendiente verificar)
prometheus  ✔ running   — http://localhost:9090
grafana     ✔ running   — http://localhost:3000 (admin/admin)
/metrics    ✔ 200 OK    — scraping Prometheus operativo
/health/live ✔ 200 OK   — healthcheck Docker operativo
```

---

## [v0.16.4] — 14 junio 2026 (noche)

### 🔑 Fix — Rotación de GROQ_API_KEY + upgrade de modelo

#### Resumen de sesión
Sesión de diagnóstico y resolución del error `401 Invalid API Key` en el NLP del bot. La key de Groq había sido expuesta accidentalmente en un chat. Se rotó la key, se actualizó el modelo a uno disponible actualmente, y se configuró SSH para Git. Ningún cambio en lógica de negocio ni base de datos.

---

#### Incidencia — Error 401 en `groq_router.py`

**Síntoma:** El bot arrancaba correctamente pero todas las llamadas a Groq devolvian:
```
Error code: 401 - {'error': {'message': 'Invalid API Key', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}}
```

**Causa raíz:** La `GROQ_API_KEY` fue expuesta en un canal externo. Adicionalmente, el modelo configurado por defecto (`llama3-8b-8192`) ya no existe en el catálogo de Groq.

**Fix:**
1. Key revocada en [console.groq.com](https://console.groq.com) y nueva key generada
2. `.env` actualizado con nueva `GROQ_API_KEY`
3. `GROQ_MODEL` cambiado de `llama3-8b-8192` (deprecado) → `llama-3.3-70b-versatile` (128k contexto, free tier)
4. `docker compose down && docker compose up -d` para forzar recarga del entorno

---

#### Modelos Groq disponibles (free tier, junio 2026)

| Modelo | Contexto | Uso recomendado |
|--------|----------|-----------------|
| `llama-3.3-70b-versatile` ✅ | 128k | **Seleccionado** — NLP, razonamiento |
| `llama-3.1-8b-instant` | 128k | Respuestas rápidas |
| `meta/llama-4-scout-17b-16e-instruct` | 512k | Contexto muy largo |
| `qwen/qwen3-32b` | 32k | Alternativa razonamiento |

---

#### Mejoras de infraestructura Git

- Remote cambiado de HTTPS → SSH: `git remote set-url origin git@github.com:alvarofernandezmota-tech/thdora.git`
- `.gitignore` ya contenia `.env` — confirmado que la key NO fue subida a GitHub

---

### 📦 Archivos de esta sesión

| Archivo | Cambio |
|---|---|
| `.env` (local, no en repo) | 🔑 Nueva GROQ_API_KEY + GROQ_MODEL=llama-3.3-70b-versatile |
| `.gitignore` | 📝 Entrada duplicada `.env` eliminada |
| `CHANGELOG.md` | 📝 Esta entrada |

---

## [v0.16.3] — 29 abril 2026 (noche)

### 🧪 Tests + Documentación — Auditoría completa

#### Resumen de sesión
Sesión de auditoría y cierre de deuda técnica. Todos los bugs corregidos en
v0.16.1 y v0.16.2 ahora tienen cobertura de test unitario.

---

## [v0.16.2] — 27 abril 2026 (noche)

### 🐛 Bugfix — B-NEW3, B-NEW5, B-NEW6

---

## [v0.16.1] — 27 abril 2026 (tarde)

### 🐛 Bugfix — Emoji franja Tarde (B1) + hora_ver_cuartos (B6)

---

## [v0.16.0] — 23 abril 2026 (tarde)

### 🔧 UX — Confirmación de borrado de cita muestra nombre + hora

---

## [v0.15.2] — 14 abril 2026 (tarde)

### ✨ NLP v2 — Cache, contexto semana, desambiguación y cierre de proyecto

---

## [v0.15.1] — 14 abril 2026

### 🔧 Fix — Conflicto de cita alineado entre API, bot /nueva y editar hora

---

## [v0.15.0] — 14 abril 2026

### ✨ Mejoras de calidad — Solapamiento real, horario visual, rendimiento y tests

---

## [v0.14.0] — 14 abril 2026
### ✨ Modo Toki: contexto real + menú en intent desconocido

---

## [v0.13.0] — 14 abril 2026
### ✨ UX, Persistencia y Personalidad

---

## [v0.12.0] — 14 abril 2026
- groq_router.py completo, handlers/nlp.py, NLP_ARQUITECTURA.md.

---

## [v0.11.0] — 13 abril 2026
- UserConfig SQLite, APScheduler, /config con notificaciones.

---

## [v0.10.0] — Abril 2026
- Bot v4 modular + UX avanzada.

---

## [v0.9.0] — Marzo 2026
- SQLiteLifeManager CRUD + FastAPI 14 endpoints.

---

## [v0.1–0.8] — Febrero–Marzo 2026
- Arquitectura base, FastAPI REST, Bot Telegram v1–v3.

---

_Última actualización: 18 junio 2026 — 21:49 CEST_
