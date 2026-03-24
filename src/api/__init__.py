"""
Módulo API de THDORA.

Expone el ecosistema THDORA como API REST con FastAPI.

Endpoints planificados (Fase 6):
    GET  /appointments/{date}  → citas del día
    POST /appointments         → crear cita
    DEL  /appointments/{id}    → eliminar cita
    GET  /habits/{date}        → hábitos del día
    POST /habits               → registrar hábito
    GET  /summary/{date}       → resumen del día

Ejecución::

    uvicorn src.api.main:app --reload --port 8000
    # Swagger UI: http://localhost:8000/docs
"""
