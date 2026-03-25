# Arquitectura de THDORA

> Estado: v0.6 — FastAPI REST + JsonLifeManager + MemoryLifeManager  
> Última actualización: 2026-03-25

---

## Visión general

THDORA es un sistema personal de gestión de vida (Life Manager) que permite registrar citas, hábitos y obtener resúmenes diarios. La arquitectura está diseñada para crecer en capas: core → API → bot → IA.

```
┌─────────────────────────────────────────────────┐
│                   CLIENTE                        │
│         (Bot Telegram / HTTP / Script)           │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              CAPA API (FastAPI)                  │
│  src/api/main.py                                 │
│  src/api/routers/appointments.py                 │
│  src/api/routers/habits.py                       │
│  src/api/models/appointment.py                   │
│  src/api/models/habit.py                         │
└────────────────────┬────────────────────────────┘
                     │ inyección de dependencia
┌────────────────────▼────────────────────────────┐
│           CAPA CORE (Business Logic)             │
│  src/core/interfaces/abstract_lifemanager.py     │
│       ↑ implementan                              │
│  src/core/impl/memory_lifemanager.py             │
│  src/core/impl/json_lifemanager.py               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              PERSISTENCIA                        │
│  datos/thdora.json  (excluido de git)            │
└─────────────────────────────────────────────────┘
```

---

## Estructura de directorios

```
thdora/
├── src/
│   ├── api/
│   │   ├── main.py                  # App FastAPI + dependency injection
│   │   ├── routers/
│   │   │   ├── appointments.py      # Endpoints de citas
│   │   │   └── habits.py            # Endpoints de hábitos
│   │   └── models/
│   │       ├── appointment.py       # Modelos Pydantic de citas
│   │       └── habit.py             # Modelos Pydantic de hábitos
│   ├── core/
│   │   ├── interfaces/
│   │   │   └── abstract_lifemanager.py  # Interfaz abstracta (ABC)
│   │   ├── impl/
│   │   │   ├── memory_lifemanager.py    # Implementación en memoria
│   │   │   └── json_lifemanager.py      # Implementación persistente JSON
│   │   └── demo.py                      # Script de demostración
│   ├── bot/                         # (Fase 7 — Telegram bot)
│   └── ai/                          # (Fase 8+ — integración IA/Ollama)
├── tests/
│   ├── unit/
│   │   ├── test_memory_lifemanager.py
│   │   └── test_json_lifemanager.py
│   ├── integration/
│   │   └── test_api.py
│   └── e2e/                         # (futuro — tests de bot)
├── docs/
│   ├── architecture/                # Este directorio
│   ├── modules/                     # Documentación por módulo
│   ├── setup/                       # Guía de instalación
│   ├── diarios/                     # Diarios de sesión
│   └── auditoria/                   # Auditorías del repositorio
├── datos/                           # Datos reales (en .gitignore)
├── docker/                          # Configuración Docker
├── pyproject.toml                   # Config proyecto + pytest + coverage
├── Makefile                         # Comandos rápidos
├── CHANGELOG.md                     # Historial de versiones
└── ROADMAP.md                       # Plan de fases
```

---

## Módulos principales

### `AbstractLifeManager` (interfaz)

Define el contrato que deben cumplir todas las implementaciones:

| Método | Descripción |
|--------|-------------|
| `create_appointment(date, time, type, notes)` | Crea una cita, devuelve UUID |
| `get_appointments(date)` | Lista citas de un día |
| `delete_appointment(date, index)` | Elimina cita por índice, devuelve bool |
| `log_habit(date, habit, value)` | Registra o sobreescribe un hábito |
| `get_habits(date)` | Devuelve dict de hábitos del día |
| `get_day_summary(date)` | Resumen completo del día |

### `MemoryLifeManager`
- Almacena datos en RAM (dict en memoria)
- Ideal para tests y entornos sin disco
- Se resetea al reiniciar el proceso

### `JsonLifeManager`
- Persiste datos en `datos/thdora.json`
- Crea el fichero y directorio automáticamente si no existen
- Formato JSON legible, estructura: `{"appointments": {...}, "habits": {...}}`

### API REST (FastAPI)
- Usa `JsonLifeManager` por defecto vía dependency injection
- `get_manager()` en `main.py` es el punto de inyección
- Los tests sobreescriben `get_manager` con instancia temporal aislada

---

## Principios de diseño

| Principio | Aplicación |
|-----------|------------|
| **Dependency Inversion** | Las capas superiores dependen de `AbstractLifeManager`, no de implementaciones concretas |
| **Open/Closed** | Añadir `JsonLifeManager` no requirió modificar nada existente |
| **Single Responsibility** | Cada módulo tiene una única responsabilidad |
| **Interface Segregation** | Las interfaces son pequeñas y cohesivas |

---

## Tipos de cita válidos

```python
VALID_TYPES = {"médica", "trabajo", "personal", "social", "deporte", "otro"}
```

---

## Formato de datos (thdora.json)

```json
{
  "appointments": {
    "2026-03-24": [
      {
        "id": "uuid-string",
        "time": "10:00",
        "type": "médica",
        "notes": "llevar analítica"
      }
    ]
  },
  "habits": {
    "2026-03-24": {
      "sueno": "7h30m",
      "THC": "0",
      "ejercicio": "60min"
    }
  }
}
```

---

## Fases del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Setup inicial, pyproject.toml, CI | ✅ |
| 2 | Estructura de directorios | ✅ |
| 3 | GitHub Actions + Makefile | ✅ |
| 4 | MemoryLifeManager + tests unitarios | ✅ |
| 5 | JsonLifeManager + persistencia | ✅ |
| 6 | FastAPI REST API + tests integración | ✅ |
| 7 | Bot Telegram (src/bot/) | 🔜 |
| 8 | Integración IA / Ollama (src/ai/) | 🔜 |
| 9 | Docker + despliegue | 🔜 |

---

## Coverage actual (2026-03-25)

| Módulo | Coverage |
|--------|----------|
| `memory_lifemanager` | 100% |
| `json_lifemanager` | 100% |
| `routers/appointments` | 100% |
| `routers/habits` | 100% |
| `api/main` | 92% |
| `interfaces/abstract_lifemanager` | 75% |
| **TOTAL** | **87%** |
