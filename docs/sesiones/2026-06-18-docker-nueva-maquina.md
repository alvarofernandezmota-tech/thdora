# 📝 Sesión 18 junio 2026 — Troubleshooting Docker en máquina nueva

**Proyecto:** THDORA (`alvarofernandezmota-tech/thdora`)
**Fecha:** 18 junio 2026, ~21:00–22:00 CEST
**Máquina:** `madre` / `varopc` / `~/Projects/thdora`
**Rama:** `main`
**Herramienta de apoyo:** Perplexity AI (MCP GitHub directo)

---

## Objetivo de la sesión

Levantar el stack THDORA completo (bot + API) en una máquina nueva donde
el repo no estaba clonado previamente. La máquina tenía el clone antiguo
en `~/dev/thdora` pero el trabajo nuevo se iba a hacer en `~/Projects/thdora`.

---

## Cronología de la sesión

### 21:00 — Estado inicial

El usuario intenta ejecutar `docker compose` y `git` desde `~` (home).
Resultado: errores inmediatos.

```bash
# Situación de partida:
pwd  # /home/varopc  (NO la carpeta del repo)
docker ps  # sin contenedores corriendo
```

### 21:05 — Bug 1: ImportError `_invalidate_cache`

**Traceback:**
```
File "/app/src/bot/handlers/nlp_disambig.py", line 25
  from src.bot.handlers.nlp import _invalidate_cache, _build_day_schedule, _time_to_min
ImportError: cannot import name '_invalidate_cache'
```

**Diagnóstico:**
- `nlp_disambig.py:25` importa tres funciones de `nlp.py`
- La imagen Docker en ejecución estaba construida sobre una versión de `nlp.py`
  que aún no tenía esas funciones
- Verificado con `grep -R "_invalidate_cache" -n .` que el código sí existía en el repo local

**Solución:**
```bash
cd ~/Projects/thdora
git reset --hard origin/main
docker compose build bot
docker compose up -d bot
```

**Aprendizaje:** `ImportError: cannot import name X` → problema de **código** o imagen desactualizada.

---

### 21:10 — Bug 2: `fatal: not a git repository`

**Síntoma:** `git fetch`, `git reset` fallaban. `docker compose` también.

**Causa:** El repo no estaba clonado en `~/Projects/thdora`.
El directorio existía pero no tenía `.git`.

**Solución:**
```bash
cd ~/Projects
git clone git@github.com:alvarofernandezmota-tech/thdora.git
cd thdora
pwd  # /home/varopc/Projects/thdora
```

**Aprendizaje:** Siempre verificar con `pwd` que estás en la carpeta correcta antes de cualquier
operación `git` o `docker compose`. Si `ls -a` no muestra `.git`, no es el repo.

---

### 21:20 — Bug 3: `.env not found`

**Mensaje de error:**
```
env file /home/varopc/Projects/thdora/.env not found:
stat /home/varopc/Projects/thdora/.env: no such file or directory
```

**Causa:** `docker-compose.yml` tiene `env_file: .env`.
Docker busca `.env` en la carpeta desde donde se ejecuta `docker compose`.
El clone nuevo no tenía `.env` (nunca va al repo por `.gitignore`).

**Solución:** Copiar el `.env` del clone anterior:
```bash
cp ~/dev/thdora/.env ~/Projects/thdora/.env
# El .env ya tiene todos los tokens: TELEGRAM_BOT_TOKEN, GROQ_API_KEY, etc.
# No hay que reconfigurarlo
```

**Aprendizaje:** Cada clone nuevo necesita su propio `.env`.
Por eso existe `.env.example` — es la plantilla para no tener que adivinar las variables.
`find ~ -maxdepth 4 -name ".env"` es útil para localizar un `.env` existente.

---

### 21:30 — Bug 4: `ModuleNotFoundError: langgraph.checkpoint.sqlite`

**Traceback completo:**
```
File "/app/src/bot/main.py", line 38
  from src.bot.handlers.stats import stats_handler
File "/app/src/bot/handlers/stats.py", line 5
  from src.agents.metrics import MetricsCollector
File "/app/src/agents/__init__.py", line 11
  from .core.graph import build_thdora_graph
File "/app/src/agents/core/graph.py", line 15
  from src.agents.core.node import _tools, agent_node
File "/app/src/agents/core/node.py", line 15
  from src.agents.memory.manager import memory_manager
File "/app/src/agents/memory/__init__.py", line 2
  from .manager import memory_manager
File "/app/src/agents/memory/manager.py", line 72
  memory_manager = ThdoraMemoryManager()
File "/app/src/agents/memory/manager.py", line 30
  from langgraph.checkpoint.sqlite import SqliteSaver
ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite'
```

**Diagnóstico:**
```bash
grep -n "langgraph" requirements.txt  # no aparece
grep -n "langgraph" pyproject.toml    # 16:langgraph>=0.2.0
```

En alguna versión de LangGraph, `checkpoint.sqlite` se separó al paquete
independiente `langgraph-checkpoint-sqlite`. El repo solo tenía `langgraph>=0.2.0`.

**Solución:** Fix aplicado directamente en GitHub por Perplexity AI (commit `bdf82f0`):
- `requirements.txt`: añadido `langgraph-checkpoint-sqlite>=2.0.0`
- `pyproject.toml`: añadido `langgraph-checkpoint-sqlite>=2.0.0` + deps LangGraph completas

Después en la máquina:
```bash
git pull origin main
docker compose build bot
docker compose up -d bot
```

**Aprendizaje:** `ModuleNotFoundError: No module named X` → problema de **dependencias**.
Buscar en `requirements.txt` / `pyproject.toml`. Nunca en el código fuente.

---

### 21:45 — Trabajo desde móvil (batería agotada)

El ordenador se quedó sin batería. Desde el móvil se:
- Generó el prompt completo para IA externa (Claude/Groq) con todos los archivos del repo
- La IA externa generó los contenidos corregidos de `requirements.txt`, `pyproject.toml`,
  `.env.example`, sección README y entrada de diario
- Perplexity AI aplicó todos los cambios directamente en GitHub vía MCP

---

## Commits de esta sesión

| SHA | Descripción |
|-----|-------------|
| `bdf82f0` | fix: añadir langgraph-checkpoint-sqlite en requirements y pyproject |
| `445ce0d` | docs: diario técnico 18 jun 2026 + entrada CHANGELOG v0.21.3 |
| *(este commit)* | docs: sesión completa + DIARIO + setup guide |

---

## Tabla resumen: tipos de error y dónde mirar

| Error | Capa | Dónde buscar | Solución tipo |
|-------|------|--------------|---------------|
| `ImportError: cannot import name X` | Código interno | El `.py` que define `X` | Actualizar código o rebuild imagen |
| `ModuleNotFoundError: No module named X` | Dependencias | `requirements.txt` / `pyproject.toml` | Añadir paquete + rebuild |
| `fatal: not a git repository` | Entorno | `pwd` — ¿estás en la carpeta? | `cd` correcto o `git clone` |
| `env file ... not found` | Docker | ¿existe `.env` en la carpeta? | `cp .env.example .env` |
| `no configuration file provided` | Docker | ¿existe `docker-compose.yml`? | `cd` a la carpeta del repo |

---

## Estado al cerrar la sesión

- ✅ Código en `main` correcto y actualizado
- ✅ Dependencias `langgraph-checkpoint-sqlite` añadidas
- ✅ Documentación completa subida al repo
- ⏳ **Pendiente (cuando cargue el ordenador):**

```bash
cd ~/Projects/thdora
git pull origin main          # trae todos los fixes y docs
cp ~/dev/thdora/.env .env     # si no lo has copiado ya
docker compose build bot      # instala langgraph-checkpoint-sqlite
docker compose up -d bot
docker compose logs -f bot    # verificar que arranca sin errores
```
