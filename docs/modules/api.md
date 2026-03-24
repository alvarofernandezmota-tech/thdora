# Módulo: src/api

## Descripción

API REST de THDORA construida con FastAPI.
Expone el `LifeManager` como servicio HTTP.

## Estado

⏳ **Fase 6 — Pendiente de implementación completa**

Actualmente sólo tiene el health check:

```
GET /       → {"status": "ok", "version": "0.4.0"}
```

## Endpoints planificados

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/appointments/{date}` | Citas del día |
| `POST` | `/appointments` | Crear cita |
| `DELETE` | `/appointments/{id}` | Eliminar cita |
| `GET` | `/habits/{date}` | Hábitos del día |
| `POST` | `/habits` | Registrar hábito |
| `GET` | `/summary/{date}` | Resumen del día |

## Ejecución

```bash
uvicorn src.api.main:app --reload
# Swagger UI: http://localhost:8000/docs
```
