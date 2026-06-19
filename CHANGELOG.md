# Changelog THDORA

## [0.22.1] — 2026-06-19

### Fixed
- `langgraph-checkpoint-sqlite>=2.0.0` ya estaba en requirements pero la imagen
  de producción se construyó antes de ese commit. Documentado y verificado.
- `fastapi` fijado a `<0.137.0` para evitar bug de compatibilidad con
  `prometheus-fastapi-instrumentator` que rompe `/health/live` y `/health/ready`.
- `src/config.py`: `Settings` ahora es lazy via `@lru_cache` + proxy `_LazySettings`.
  Elimina los 11 errores de colección en CI cuando no hay `.env`.
- `docker/.env.docker.example`: añadido `THDORA_API_URL=http://thdora:8000` y
  documentado como PRIMER PASO obligatorio antes de arrancar el stack.

### Changed
- `tests.yml`: CI ahora inyecta variables dummy para que pytest no necesite
  credenciales reales en GitHub Actions.
- `deploy.yml`: ya tenía `docker compose up -d --build` correcto. Confirmado.

## [0.22.0] — 2026-06-18

### Fixed (Sprint 5 — 10 bugs Docker)
- B1: `/health/live` añadido a FastAPI
- B2: `THDORA_DB_URL` unificado (antes era `THDORA_DB_PATH`)
- B3: `curl` instalado en Dockerfile
- B4: `/app/logs` creado en imagen
- B5: `setup_prometheus()` llamado en `main.py`
- B6: `PicklePersistence` con ruta absoluta `/app/data/bot_persistence.pkl`
- B7: `docker/Dockerfile` marcado como LEGACY
- B8: servicio `bot` añadido a `docker-compose.yml`
- B9: `pyproject.toml` sincronizado con `requirements.txt`
- B10: emoji 🌆 corregido en `keyboards.py`
