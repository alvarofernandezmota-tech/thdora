# THDORA — Agent Platform v2

> **Esta rama NO toca el bot actual.** Es el scaffold completo de la nueva plataforma multi-tenant.
> El bot actual en `main` sigue funcionando en producción.

## Stack
- Python 3.12 + FastAPI
- PostgreSQL 16 + pgvector
- Redis (cache + colas)
- LangGraph (orquestación de agentes)
- Docker Compose

## Estructura
```
platform/
├── core/          # Config, DB, seguridad
├── agents/        # Agent Factory — modelos, CRUD, orquestador
├── tools/         # Tool Registry + implementaciones
├── api/           # Endpoints FastAPI
├── migrations/    # SQL DDL
└── docker-compose.platform.yml
```

## Arrancar (desarrollo)
```bash
cd platform
cp .env.example .env
docker compose -f docker-compose.platform.yml up -d
uvicorn main:app --reload
```

## Flujo básico
1. `POST /api/agents/` → Crea agente con system_prompt + tools
2. `POST /api/chat/{agent_id}` → Habla con el agente
3. `POST /api/tools/` → Registra un tool nuevo
4. `POST /api/agents/{id}/tools/attach` → Asigna tool al agente
