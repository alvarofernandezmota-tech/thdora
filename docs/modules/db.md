# 🖴 Módulo `src/db/` — Persistencia SQLite

> **Navegación:** [INDEX](../INDEX.md) · [CHANGELOG](../../CHANGELOG.md) · [ROADMAP](../../ROADMAP.md)

**Fase:** F9 | **Versión:** 0.8.0 | **Estado:** ✅ Implementado

---

## ¿Qué hace este módulo?

Provee persistencia real a THDORA. Antes de F9, los datos vivían en RAM
(MemoryLifeManager) o en JSON (JsonLifeManager) y se perdían al reiniciar.
Ahora los datos se guardan en `data/thdora.db` (SQLite) y sobreviven reinicios.

---

## Estructura

```
src/db/
├── __init__.py              ← exports del módulo
├── base.py                  ← engine, session, Base, init_db()
├── models.py                ← ORM: Appointment + Habit
└── migrations/
    └── README.md             ← Alembic pendiente F9.1
```

---

## Modelos

### `Appointment`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | autoincremental |
| `date` | String(10) | YYYY-MM-DD, indexado |
| `time` | String(5) | HH:MM |
| `name` | String(200) | nombre/descripción |
| `type` | String(50) | médica/personal/trabajo/otra |
| `notes` | Text | notas opcionales |
| `index` | Integer | ordinal por día (1, 2, 3…) |

### `Habit`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | autoincremental |
| `date` | String(10) | YYYY-MM-DD, indexado |
| `habit` | String(100) | nombre del hábito |
| `value` | String(100) | valor ("8h", "2L", "30min") |

---

## `SQLiteLifeManager`

Implementa `AbstractLifeManager` con SQLite. Métodos:

### Citas
- `get_appointments(date)` → lista ordenada por hora
- `create_appointment(date, time, type, notes, name)` → dict con index
- `delete_appointment(date, index)` → bool
- `update_appointment(date, index, ...)` → dict | None
- `get_appointments_range(date_from, date_to)` → lista (para /agenda)
- `get_upcoming_appointments(from_date, limit)` → lista (para /proximas)

### Hábitos
- `get_habits(date)` → dict {nombre: valor}
- `log_habit(date, habit, value)` → upsert — crea o actualiza
- `delete_habit(date, habit)` → bool
- `update_habit(date, habit, value)` → dict | None
- `get_habits_range(date_from, date_to)` → dict por fecha
- `get_summary(date)` → citas + hábitos del día

---

## ¿Por qué SQLite y no PostgreSQL?

SQLite es la elección correcta para THDORA ahora mismo:
- Un solo usuario — no hay concurrencia real
- Cero configuración — archivo local, sin servidor
- Fácil de migrar a PostgreSQL en F12 si se despliega en VPS
- Viene incluido en Python — sin dependencia extra

---

## Próximos pasos (F9.1)

- [ ] Configurar Alembic para migraciones incrementales
- [ ] Tests unitarios de SQLiteLifeManager
- [ ] Conectar routers FastAPI a SQLiteLifeManager (reemplazar MemoryLifeManager)
- [ ] Script de migración de datos JSON existentes a SQLite

---

_Creado: 27 marzo 2026 — 22:16 CET_
