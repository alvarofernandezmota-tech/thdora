# 📝 Sesión 18 junio 2026 — Troubleshooting Docker en máquina nueva

**Proyecto:** THDORA (`alvarofernandezmota-tech/thdora`)
**Fecha:** 18 junio 2026, ~21:00–22:00 CEST
**Máquina:** `madre` / `varopc` / `~/Projects/thdora`
**Rama:** `main`
**Herramienta de apoyo:** Perplexity AI (MCP GitHub directo) + Groq (auditoría preventiva)

---

## Objetivo de la sesión

Levantar el stack THDORA completo (bot + API) en una máquina nueva donde
el repo no estaba clonado previamente.

---

## Bugs resueltos (cronología)

### Bug 1 — `ImportError: cannot import name '_invalidate_cache'`

**Traceback:**
```
from src.bot.handlers.nlp import _invalidate_cache, _build_day_schedule, _time_to_min
ImportError: cannot import name '_invalidate_cache'
```
**Causa:** Imagen Docker construida antes de que `nlp.py` tuviera esas funciones.
**Fix:** `git reset --hard origin/main` + `docker compose build bot`
**Capa:** Código interno / imagen desactualizada

---

### Bug 2 — `fatal: not a git repository`

**Causa:** Ejecutar `git` y `docker compose` desde `~` en vez de `~/Projects/thdora`.
**Fix:** `cd ~/Projects/thdora` antes de cualquier comando.
**Capa:** Entorno / directorio incorrecto

---

### Bug 3 — `.env not found`

**Causa:** El `.env` no se copia al hacer `git clone` (está en `.gitignore`).
**Fix:** `cp ~/dev/thdora/.env ~/Projects/thdora/.env`
**Capa:** Docker / configuración de entorno

---

### Bug 4 — `ModuleNotFoundError: langgraph.checkpoint.sqlite`

**Causa:** `langgraph>=0.2.0` ya no incluye el checkpointer SQLite — paquete separado.
**Fix:** Añadido `langgraph-checkpoint-sqlite>=2.0.0` en `requirements.txt` y `pyproject.toml`.
**Commits:** `bdf82f0`
**Capa:** Dependencias

---

### Bug 5 — `data/` no existe al instanciar `SqliteSaver` (preventivo)

**Archivo:** `src/agents/memory/manager.py:30`
**Causa:** `SqliteSaver.from_conn_string("data/thdora_memory.db")` falla si `data/` no existe
en el contenedor en el momento del import (antes de que `main.py` haga su propio `os.makedirs`).
**Fix:** Añadido `os.makedirs("data", exist_ok=True)` al inicio de `ThdoraMemoryManager.__init__`.
**Commit:** `6f2caaf`
**Capa:** Código / orden de inicialización

---

### Bug 6 — `_check_api()` bloqueante si API no está lista (preventivo)

**Archivo:** `src/bot/main.py:141`
**Causa:** `asyncio.run(_check_api())` se ejecuta antes de `build_app()`. Si la API
tarda en levantar (race condition en Docker Compose), el bot abortá el arranque.
**Fix:** `_check_api()` ahora tiene 3 reintentos con backoff exponencial (2s, 4s)
y loguea un warning si falla, pero **nunca aborta el arranque**.
**Commit:** `6f2caaf`
**Capa:** Resiliencia / infraestructura Docker

---

### Bug 7 — `GITHUB_TOKEN` obligatorio causa `ValidationError` (preventivo)

**Archivo:** `src/config.py:40`
**Causa:** `GITHUB_TOKEN: str = Field(min_length=1)` — pydantic-settings lanza
`ValidationError` al arrancar si la variable no está en `.env` o está vacía.
El comando `/diario` necesita el token, pero el **resto del bot es independiente**.
**Fix:** Cambiado a `GITHUB_TOKEN: str = ""` (valor por defecto vacío, opcional).
Si está vacío, solo falla `/diario`, no el arranque completo.
**Commit:** *(este commit)*
**Capa:** Configuración / validación Pydantic

---

### Bug 8 — `MetricsCollector` — estado

**Archivo:** `src/agents/metrics.py`
**Evaluación:** `MetricsCollector` no tiene estado a nivel módulo — solo define la clase.
El singleton `_metrics = MetricsCollector()` está en `stats.py` pero no ejecuta
código bloqueante al instanciarse. **No es un riesgo real de arranque.**
**Acción:** Ninguna. Documentado como falsa alarma.

---

## Commits de esta sesión

| SHA | Descripción |
|-----|-------------|
| `bdf82f0` | fix: langgraph-checkpoint-sqlite en requirements y pyproject |
| `445ce0d` | docs: diario técnico 18 jun + CHANGELOG v0.21.3 |
| `fddd55b` | docs: sesión completa + DIARIO + setup guide |
| `6f2caaf` | fix: manager.py os.makedirs + main.py _check_api no-bloqueante |
| *(este)* | fix: GITHUB_TOKEN opcional + docs actualizados |

---

## Tabla resumen: tipos de error y dónde mirar

| Error | Capa | Dónde buscar | Solución tipo |
|-------|------|--------------|---------------|
| `ImportError: cannot import name X` | Código interno | El `.py` que define `X` | Actualizar código o rebuild imagen |
| `ModuleNotFoundError: No module named X` | Dependencias | `requirements.txt` / `pyproject.toml` | Añadir paquete + rebuild |
| `ValidationError` en Pydantic | Configuración | `src/config.py` + `.env` | Añadir variable o hacerla opcional |
| `fatal: not a git repository` | Entorno | `pwd` — ¿estás en la carpeta? | `cd` correcto o `git clone` |
| `env file ... not found` | Docker | ¿existe `.env` en la carpeta? | `cp .env.example .env` |
| `no configuration file provided` | Docker | ¿existe `docker-compose.yml`? | `cd` a la carpeta del repo |
| `attempt to write a readonly database` | Docker / permisos | UID mismatch en `./data` | `sudo chown -R 1000:1000 ./data` |

---

## Estado al cerrar la sesión

- ✅ 4 bugs reales resueltos + 3 preventivos aplicados
- ✅ 1 falsa alarma descartada (MetricsCollector)
- ✅ Toda la documentación actualizada en el repo
- ⏳ **Pendiente cuando cargue el ordenador:**

```bash
cd ~/Projects/thdora
git pull origin main
docker compose build bot
docker compose up -d bot
docker compose logs -f bot
```
