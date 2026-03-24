# 🗺️ Mapa del repositorio — thdora

> **Navegación rápida:** [README](../../README.md) · [Índice docs](../INDEX.md) · [ROADMAP](../../ROADMAP.md) · [ARCHITECTURE](./ARCHITECTURE.md)

Este documento es la **referencia de orientación del repo**. Antes de empezar cualquier fase, leerlo para saber exactamente dónde está cada cosa, qué hace y cómo se conecta con el resto.

**Regla:** si no sabes dónde poner algo nuevo → consulta este mapa primero.

---

## 📁 Raíz del repo

| Archivo / Carpeta | Tipo | Propósito | Estado |
|-------------------|------|-----------|--------|
| `README.md` | doc | Portada del repo. Navegación rápida, qué es thdora, hardware, estado del proyecto | ✅ |
| `ROADMAP.md` | doc | Plan por fases con progreso visual y enlaces a docs y thea-ia | ✅ |
| `CHANGELOG.md` | doc | Historial real de cambios por versión | ✅ |
| `pyproject.toml` | config | Dependencias Python, metadatos del paquete, configuración pytest/black | ✅ |
| `Makefile` | config | Comandos de desarrollo: `make test`, `make lint`, `make run` | ✅ |
| `.gitignore` | config | Excluye `.venv/`, `datos/thdora.json`, `__pycache__/`, `.env` | ✅ |
| `src/` | código | Todo el código fuente Python | ✅ |
| `tests/` | código | Suite de tests (pytest) | ✅ |
| `docs/` | doc | Toda la documentación del proyecto | ✅ |
| `datos/` | datos | Persistencia JSON local — **nunca va al repo** | ✅ |
| `docker/` | config | Dockerfile + docker-compose para deploy | ⏳ Fase 10 |
| `.github/` | config | GitHub Actions CI/CD | ✅ |

---

## 📁 `src/` — Código fuente

### `src/core/` — Lógica de negocio central

> **Regla:** aquí vive la lógica pura. Sin dependencias de FastAPI, Telegram ni Ollama.

| Subcarpeta / Archivo | Propósito | Estado | Doc relacionada |
|----------------------|-----------|--------|-----------------|
| `core/interfaces/` | Contratos ABC — define QUÉ hace el sistema | ✅ | [core.md](../modules/core.md) |
| `core/interfaces/abstract_lifemanager.py` | Interfaz base con métodos abstractos: citas, hábitos, resumen | ✅ | [core.md](../modules/core.md) |
| `core/impl/` | Implementaciones concretas de las interfaces | ✅ | [core.md](../modules/core.md) |
| `core/impl/memory_lifemanager.py` | Almacena datos en RAM. Para tests y desarrollo | ✅ 13 tests | [core.md](../modules/core.md) |
| `core/impl/json_lifemanager.py` | Almacena datos en `datos/thdora.json` | ⏳ **Fase 5** | [ADR-003](./decisions/ADR-003-json-persistence.md) |
| `core/impl/sql_lifemanager.py` | Almacena datos en PostgreSQL con SQLAlchemy | ⏳ **Fase 11** | [ADR pendiente] |

**Jerarquía de implementaciones:**
```
AbstractLifeManager (ABC)
    ├── MemoryLifeManager   → tests, desarrollo local
    ├── JsonLifeManager     → uso personal (Fase 5)
    └── SqlLifeManager      → producción / multiusuario (Fase 11)
```

### `src/api/` — FastAPI REST

> Expone la lógica de `core/` como endpoints HTTP.

| Archivo | Propósito | Estado | Doc relacionada |
|---------|-----------|--------|-----------------|
| `api/main.py` | App FastAPI + health check `/health` | ✅ esqueleto | [api.md](../modules/api.md) |
| `api/routers/` | Endpoints organizados por dominio | ⏳ **Fase 6** | [api.md](../modules/api.md) |
| `api/models/` | Pydantic models para validación | ⏳ **Fase 6** | [api.md](../modules/api.md) |

**Referencia thea-ia:** [`src/theaia/api/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/api)

### `src/bot/` — Bot Telegram

> Interfaz de usuario principal. Conecta Telegram con `core/` vía `api/`.

| Archivo | Propósito | Estado | Doc relacionada |
|---------|-----------|--------|-----------------|
| `bot/__init__.py` | Módulo vacío | ⏳ **Fase 7** | — |
| `bot/telegram_bot.py` | Handler principal del bot | ⏳ **Fase 7** | — |
| `bot/handlers/` | Handlers por comando: `/citas`, `/nueva`, `/habito` | ⏳ **Fase 7** | — |

**Referencia thea-ia:** [`src/theaia/adapters/telegram/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/adapters/telegram) — `bot.py` (8KB) + `telegram_adapter.py` (14KB)

### `src/ai/` — Capa de IA local

> Integración con Ollama. Conecta el modelo local con el bot.

| Archivo | Propósito | Estado | Doc relacionada |
|---------|-----------|--------|-----------------|
| `ai/__init__.py` | Módulo vacío | ⏳ **Fase 8** | — |
| `ai/ollama_client.py` | Cliente para Ollama API en localhost:11434 | ⏳ **Fase 8** | [setup entorno](../setup/entorno-local.md) |
| `ai/agents/` | Agentes especializados (GitHub, vida personal) | ⏳ **Fase 9** | — |
| `ai/orchestrator.py` | Coordina qué agente responde cada mensaje | ⏳ **Fase 9** | — |

**Referencia thea-ia:** [`src/theaia/core/nlp_engine.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/nlp_engine.py) (15KB) · [`orchestrator.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/orchestrator.py) (14KB)

---

## 📁 `tests/` — Suite de tests

| Subcarpeta | Propósito | Estado |
|------------|-----------|--------|
| `tests/unit/` | Tests unitarios por módulo — sin dependencias externas | ✅ 13 tests |
| `tests/integration/` | Tests que integran varios módulos (ej: API + core) | ⏳ Fase 6 |
| `tests/e2e/` | Tests end-to-end (bot → api → core → datos) | ⏳ Fase 7+ |

**Cómo ejecutar:**
```bash
pytest tests/              # todos
pytest tests/unit/         # solo unitarios
pytest --cov=src tests/    # con cobertura
```

---

## 📁 `docs/` — Documentación

| Carpeta / Archivo | Propósito | Estado |
|-------------------|-----------|--------|
| `docs/INDEX.md` | **Índice maestro** — punto de entrada a toda la doc | ✅ |
| `docs/architecture/ARCHITECTURE.md` | Arquitectura general: capas, principios, flujo | ✅ |
| `docs/architecture/repo-map.md` | **Este archivo** — mapa de carpetas y responsabilidades | ✅ |
| `docs/architecture/decisions/` | ADRs — una decisión arquitectónica por archivo | ✅ 4 ADRs |
| `docs/setup/entorno-local.md` | Guía completa de instalación del entorno local | ✅ |
| `docs/auditoria/thea-ia.md` | Inventario de thea-ia y plan de reutilización | ✅ |
| `docs/modules/core.md` | Documentación del módulo `src/core/` | ✅ |
| `docs/modules/api.md` | Documentación del módulo `src/api/` | ✅ |
| `docs/diarios/` | Diario técnico diario — uno por día trabajado | ✅ |

### ADRs existentes

| ADR | Decisión |
|-----|----------|
| [ADR-001](./decisions/ADR-001-monorepo.md) | Monorepo |
| [ADR-002](./decisions/ADR-002-abc-interfaces.md) | Interfaces ABC |
| [ADR-003](./decisions/ADR-003-json-persistence.md) | JSON como primera persistencia |
| [ADR-004](./decisions/ADR-004-relacion-thea-ia.md) | thdora independiente de thea-ia |

---

## 📁 `datos/` — Persistencia local

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `datos/thdora.json` | Base de datos JSON — citas y hábitos | ⏳ Fase 5 |
| `datos/.gitkeep` | Mantiene la carpeta en git sin exponer datos | ✅ |

> ⚠️ **`datos/thdora.json` está en `.gitignore`** — los datos personales nunca van al repo.

---

## 📁 `docker/` — Contenedores

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `docker/Dockerfile` | Imagen de thdora | ⏳ Fase 10 |
| `docker/docker-compose.yml` | Stack completo: thdora + PostgreSQL | ⏳ Fase 10-11 |

---

## 📁 `.github/` — CI/CD

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `.github/workflows/tests.yml` | Tests automáticos en cada push a main | ✅ |

---

## 🔄 Flujo de datos — cómo se conecta todo

```
Usuario (Telegram / CLI)
        ↓
   src/bot/           ← recibe el mensaje
        ↓
   src/ai/            ← (Fase 8+) interpreta la intención con Ollama
        ↓
   src/api/           ← (Fase 6+) o directamente
        ↓
   src/core/          ← lógica de negocio pura
        ↓
   datos/             ← persistencia (JSON → SQL en el futuro)
```

---

## 🗄️ Hoja de ruta de persistencia

| Fase | Tecnología | Implementación | Herramientas |
|------|-----------|----------------|-------------|
| **Fase 5** | JSON local | `JsonLifeManager` | stdlib Python (`json`, `pathlib`) |
| **Fase 11** | PostgreSQL | `SqlLifeManager` | SQLAlchemy + Alembic + pgAdmin |

### Lo que necesitará la Fase 11 (BD real)

Cuando llegue la migración a PostgreSQL habrá que instalar y configurar:
- **PostgreSQL** — servidor de base de datos
- **pgAdmin** — interfaz visual para gestionar la BD
- **SQLAlchemy** — ORM Python (referencia: [`thea-ia/database/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/database))
- **Alembic** — migraciones de esquema (referencia: `thea-ia/alembic.ini`)
- Migración de datos: `thdora.json` → tablas PostgreSQL

Todo esto se documentará paso a paso en `docs/setup/postgresql.md` cuando llegue la Fase 11. **No antes.**

---

## 🌐 Ecosistema completo

```
alvarofernandezmota-tech/
├── thea-ia     → proyecto original (intacto, historia, cantera de código)
│               → NLP engine, orchestrator, router, Telegram, SQLAlchemy
├── thdora      → este repo (proyecto activo)
│               → evolución consciente de thea-ia
└── personal    → diario personal y vida
```

Ver [ADR-004](./decisions/ADR-004-relacion-thea-ia.md) para la decisión completa sobre la relación entre ambos.

---

_Creado: 24 marzo 2026 — actualizar con cada nueva carpeta o cambio estructural relevante_
