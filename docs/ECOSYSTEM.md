# 🗺️ MAPA DEL ECOSISTEMA — THDORA

> Documento vivo. Refleja el estado real del ecosistema en todo momento.

---

## Visión

THDORA es un **Sistema Operativo de Agentes IA**.
La arquitectura es una plantilla: cambiando system_prompt + tools + handlers
tienes un agente completamente distinto desplegado en minutos.

**Objetivo final:** Plataforma donde cualquier persona o empresa pueda desplegar
su propio agente IA personalizado sin tocar código.

---

## Componentes actuales

### 1. THDORA Bot v1 (Producción)

| Atributo | Valor |
|---|---|
| **Rama** | `main` |
| **Estado** | ✅ Producción 24/7 |
| **Stack** | Python + FastAPI + SQLite + Docker + Groq API |
| **LLM** | llama-3.3-70b-versatile (128k contexto) via Groq |
| **Servidor** | Doméstico (Madre) — Arch Linux / Hyprland |
| **Interfaz** | Telegram Bot |

**Qué hace:**
- Gestión de citas médicas con NLP en texto libre
- Hábitos diarios y seguimiento
- Scheduler de notificaciones (buenos días + recordatorios noche)
- 9 comandos + flujos conversacionales
- Historial en BD propia

**Archivos clave:**
- `bot.py` / `main.py` — Entry point
- `handlers/` — Lógica de cada comando
- `nlp/` — Procesamiento de lenguaje natural
- `scheduler.py` — Notificaciones automáticas
- `database.py` — SQLite
- `docker-compose.yml` — Infraestructura producción

---

### 2. Agent Platform v2 (En desarrollo)

| Atributo | Valor |
|---|---|
| **Rama** | `feature/agent-platform-v2` |
| **Estado** | 🔨 Scaffold creado — pendiente arrancar |
| **Stack** | Python 3.12 + FastAPI + PostgreSQL + pgvector + Redis + LangGraph |
| **LLM** | Groq (producción) / Ollama (local) |
| **Infra** | Docker Compose aislado (puertos distintos al v1) |

**Qué hace (objetivo):**
- Agent Factory: crear agentes sin código (INSERT en BD)
- Tool Registry dinámico: tools como JSON schemas en BD
- Orquestador LangGraph: carga config por UUID + tool calling
- Multi-tenant: cada usuario/empresa tiene sus propios agentes
- Memoria semántica: pgvector para contexto a largo plazo
- Redis cache: configs de agentes cacheadas (TTL 5 min)

**Carpeta:** `platform/`

**Puertos (no colisionan con v1):**
- API: `8001`
- PostgreSQL: `5433`
- Redis: `6380`

---

## Stack tecnológico global

```
Capa              | v1 (Producción)          | v2 (En desarrollo)
------------------|--------------------------|-----------------------------
API               | FastAPI                  | FastAPI
Bot               | python-telegram-bot      | python-telegram-bot (router)
LLM               | Groq (llama-3.3-70b)     | Groq + Ollama fallback
Orquestación      | Monolítico               | LangGraph
BD principal      | SQLite                   | PostgreSQL 16 + pgvector
Cache             | —                        | Redis 7
Infra             | Docker Compose           | Docker Compose (aislado)
OS                | Arch Linux / Hyprland    | Arch Linux / Hyprland
Servidor          | Doméstico (Madre)        | Doméstico (Madre)
```

---

## Decisiones de arquitectura

### ¿Por qué LangGraph en v2?
Es el estándar 2026 para agentes con estado persistente.
Permite grafos dirigidos con checkpointing, streaming y human-in-the-loop.
Alternativas evaluadas: CrewAI (más rápido de prototipear), Phidata (más RAG-focused).

### ¿Por qué pgvector en lugar de Qdrant/Chroma?
Menos infraestructura. Al estar en PostgreSQL, la memoria semántica vive
en la misma BD que el resto de datos. Sin servicio adicional que mantener.

### ¿Por qué Groq en lugar de OpenAI?
Coste (~50x más barato), velocidad (inferencia más rápida), y
llama-3.3-70b-versatile con 128k de contexto es más que suficiente.

### ¿Por qué SQLite en v1 y PostgreSQL en v2?
SQLite es suficiente para un bot personal con un usuario. PostgreSQL
es necesario para multi-tenant, concurrencia real y pgvector.

---

## Hoja de ruta

```
Semana 1  → Arrancar platform v2, verificar schema, probar endpoints
Semana 2  → Tool Registry funcional + 5 tools built-in
Semana 3  → Migrar bot v1 al orquestador v2
Semana 4  → Tool Calling dinámico (el gran diferenciador)
Semana 5  → Panel admin mínimo
Semana 6  → Primer cliente beta real
Futuro    → Multi-canal, Marketplace de agentes, Monetización SaaS
```
