# Módulo: src/core

## Descripción

Núcleo del ecosistema THDORA. Contiene la lógica de negocio,
las interfaces abstractas y las implementaciones concretas.

## Estructura

```
src/core/
├── __init__.py
├── interfaces/
│   ├── __init__.py
│   └── abstract_lifemanager.py   ← AbstractLifeManager
├── impl/
│   ├── __init__.py
│   └── memory_lifemanager.py     ← MemoryLifeManager
└── demo.py                       ← demo de uso
```

## Interfaces

### AbstractLifeManager

Contrato ABC principal. Toda implementación debe heredar de ella.

| Método | Descripción | Returns |
|--------|-------------|--------|
| `create_appointment(date, time, type, notes)` | Crea cita | `UUID` |
| `get_appointments(date)` | Citas del día | `List[Dict]` |
| `log_habit(date, habit, value)` | Registra hábito | `bool` |
| `get_habits(date)` | Hábitos del día | `Dict[str,str]` |
| `get_day_summary(date)` | Resumen completo | `Dict` |

## Implementaciones

### MemoryLifeManager

| Característica | Valor |
|----------------|-------|
| Almacenamiento | RAM (dict Python) |
| Persistencia | ❌ No persiste |
| Velocidad | O(1) todas las operaciones |
| Uso recomendado | Desarrollo y testing |

### JsonLifeManager *(pendiente — Fase 5)*

| Característica | Valor |
|----------------|-------|
| Almacenamiento | `datos/citas.json` |
| Persistencia | ✅ Persiste entre sesiones |
| Uso recomendado | Producción local |
