# Módulo: src/api

> Estado: ✅ Fase 6 completada  
> Última actualización: 2026-03-25

## Descripción

API REST de THDORA construida con FastAPI. Expone el `JsonLifeManager` como servicio HTTP con validación Pydantic en todos los endpoints.

## Estructura

```
src/api/
├── __init__.py
├── main.py                  # App FastAPI + dependency injection
├── routers/
│   ├── __init__.py
│   ├── appointments.py      # Endpoints de citas
│   └── habits.py            # Endpoints de hábitos
└── models/
    ├── __init__.py
    ├── appointment.py       # Modelos Pydantic de citas
    └── habit.py             # Modelos Pydantic de hábitos
```

## Endpoints implementados

### Health Check

| Método | Ruta | Status | Descripción |
|--------|------|--------|-------------|
| `GET` | `/` | 200 | Health check del servicio |

```json
{"status": "ok"}
```

### Citas (Appointments)

| Método | Ruta | Status | Descripción |
|--------|------|--------|-------------|
| `POST` | `/appointments/{date}` | 201 | Crear cita |
| `GET` | `/appointments/{date}` | 200 | Listar citas del día |
| `DELETE` | `/appointments/{date}/{index}` | 204 | Eliminar cita por índice |

**POST body:**
```json
{
  "time": "10:00",
  "type": "médica",
  "notes": "llevar analítica"
}
```

**Errores:**
- `422` — tipo inválido, hora inválida o fecha inválida
- `404` — índice fuera de rango al eliminar

### Hábitos (Habits)

| Método | Ruta | Status | Descripción |
|--------|------|--------|-------------|
| `POST` | `/habits/{date}` | 201 | Registrar hábito |
| `GET` | `/habits/{date}` | 200 | Listar hábitos del día |

**POST body:**
```json
{
  "habit": "sueno",
  "value": "7h30m"
}
```

## Dependency Injection

`main.py` expone `get_manager()` que devuelve el `JsonLifeManager` con el fichero de datos real. Los tests sobreescriben esta dependencia con una instancia temporal:

```python
app.dependency_overrides[JsonLifeManager] = lambda: test_manager
```

## Ejecución

```bash
uvicorn src.api.main:app --reload
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
```

## Coverage

| Fichero | Coverage |
|---------|----------|
| `routers/appointments.py` | 100% |
| `routers/habits.py` | 100% |
| `main.py` | 92% |
| `models/appointment.py` | 100% |
| `models/habit.py` | 100% |
