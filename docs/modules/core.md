# Módulo: src/core

> Estado: ✅ Fase 4 y 5 completadas  
> Última actualización: 2026-03-25

## Descripción

Núcleo del ecosistema THDORA. Contiene la lógica de negocio, las interfaces abstractas y las implementaciones concretas. Es completamente independiente de FastAPI, Telegram o cualquier otro framework.

## Estructura

```
src/core/
├── __init__.py
├── interfaces/
│   ├── __init__.py
│   └── abstract_lifemanager.py   ← AbstractLifeManager (ABC)
├── impl/
│   ├── __init__.py
│   ├── memory_lifemanager.py     ← MemoryLifeManager
│   └── json_lifemanager.py       ← JsonLifeManager
└── demo.py                       ← script de demostración
```

## Interfaz: AbstractLifeManager

Contrato ABC principal. Toda implementación debe heredar de ella.

| Método | Descripción | Returns |
|--------|-------------|--------|
| `create_appointment(date, time, type, notes)` | Crea cita, valida hora y tipo | `UUID` |
| `get_appointments(date)` | Citas del día | `List[Dict]` |
| `delete_appointment(date, index)` | Elimina por índice | `bool` |
| `log_habit(date, habit, value)` | Registra o sobreescribe hábito | `bool` |
| `get_habits(date)` | Hábitos del día | `Dict[str, str]` |
| `get_day_summary(date)` | Resumen completo | `Dict` |

## Implementaciones

### MemoryLifeManager ✅

| Característica | Valor |
|----------------|-------|
| Almacenamiento | RAM (dict Python) |
| Persistencia | ❌ No persiste al reiniciar |
| Velocidad | O(1) todas las operaciones |
| Uso recomendado | Tests unitarios, desarrollo |
| Coverage | 100% |

### JsonLifeManager ✅

| Característica | Valor |
|----------------|-------|
| Almacenamiento | `datos/thdora.json` |
| Persistencia | ✅ Persiste entre sesiones |
| Velocidad | O(n) en guardado (serializa todo el fichero) |
| Uso recomendado | Producción local |
| Coverage | 100% |

## Validaciones del core

### Formato de hora
Debe cumplir el patrón `HH:MM` (24h). Ejemplos válidos: `09:00`, `14:30`, `23:59`.

```python
if not re.match(r'^\d{2}:\d{2}$', time):
    raise ValueError("Formato de hora inválido")
```

### Tipos de cita válidos

```python
VALID_TYPES = {"médica", "trabajo", "personal", "social", "deporte", "otro"}
```

## Ejecución de la demo

```bash
python src/core/demo.py
```
