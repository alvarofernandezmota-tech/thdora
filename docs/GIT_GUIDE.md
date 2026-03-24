# thdora 2.0 — Guía de PRs

## Estructura de ficheros por tarea

### TAREA 1 — feat/delete-appointment
- `abstract_lifemanager.py` → `src/core/interfaces/abstract_lifemanager.py`
- `memory_lifemanager.py`   → `src/core/impl/memory_lifemanager.py`
- `test_memory_lifemanager.py` → `tests/unit/test_memory_lifemanager.py`

### TAREA 2 — feat/validate-appointment  
- `memory_lifemanager.py`      → `src/core/impl/memory_lifemanager.py`
- `test_memory_lifemanager.py` → `tests/unit/test_memory_lifemanager.py`

### TAREA 3 — feat/json-lifemanager
- `json_lifemanager.py`    → `src/core/impl/json_lifemanager.py`
- `test_json_lifemanager.py` → `tests/unit/test_json_lifemanager.py`
- `__init__impl.py`        → `src/core/impl/__init__.py`

### TAREA 4 — feat/fastapi-endpoints
- `appointment.py`         → `src/api/models/appointment.py`
- `habit.py`               → `src/api/models/habit.py`
- `appointments_router.py` → `src/api/routers/appointments.py`
- `habits_router.py`       → `src/api/routers/habits.py`
- `main.py`                → `src/api/main.py`
- `test_api.py`            → `tests/integration/test_api.py`
  También crear: `src/api/models/__init__.py`, `src/api/routers/__init__.py`

---

## Comandos git

### TAREA 1

```bash
cd ~/projects/thdora
git checkout main && git pull
git checkout -b feat/delete-appointment

# Copiar ficheros de task1 a sus rutas definitivas
# (reemplaza /path/to/downloads/ con donde descargaste los ficheros)
cp abstract_lifemanager.py src/core/interfaces/abstract_lifemanager.py
cp memory_lifemanager.py   src/core/impl/memory_lifemanager.py
cp test_memory_lifemanager.py tests/unit/test_memory_lifemanager.py

pytest tests/ -v
# ✅ Todos deben pasar antes de commitear

git add src/core/interfaces/abstract_lifemanager.py
git add src/core/impl/memory_lifemanager.py
git add tests/unit/test_memory_lifemanager.py
git commit -m "feat: add delete_appointment to AbstractLifeManager and MemoryLifeManager

- Add delete_appointment(date, index) abstract method to AbstractLifeManager
- Implement in MemoryLifeManager with IndexError on invalid index
- Add TestDeleteAppointment class with 5 tests (valid, IndexError, empty day, negative)"

git push origin feat/delete-appointment
# Abrir PR en GitHub: feat/delete-appointment → main
```

### TAREA 2 (esperar a que T1 esté mergeado)

```bash
git checkout main && git pull
git checkout -b feat/validate-appointment

cp memory_lifemanager.py   src/core/impl/memory_lifemanager.py
cp test_memory_lifemanager.py tests/unit/test_memory_lifemanager.py

pytest tests/ -v
# ✅ Todos deben pasar

git add src/core/impl/memory_lifemanager.py
git add tests/unit/test_memory_lifemanager.py
git commit -m "feat: add input validation to create_appointment

- Validate time format with HH:MM regex (00:00-23:59)
- Validate type against VALID_TYPES frozenset (médica/personal/trabajo/otra)
- Raise ValueError with descriptive messages
- Add parametrize test covering all valid types
- Add ValueError tests for invalid time and type"

git push origin feat/validate-appointment
# Abrir PR: feat/validate-appointment → main
```

### TAREA 3 (esperar a que T1 y T2 estén mergeados)

```bash
git checkout main && git pull
git checkout -b feat/json-lifemanager

cp json_lifemanager.py      src/core/impl/json_lifemanager.py
cp test_json_lifemanager.py tests/unit/test_json_lifemanager.py
cp __init__impl.py          src/core/impl/__init__.py

pytest tests/ -v
# ✅ Todos deben pasar

git add src/core/impl/json_lifemanager.py
git add src/core/impl/__init__.py
git add tests/unit/test_json_lifemanager.py
git commit -m "feat: implement JsonLifeManager (Fase 5)

- Persist appointments and habits to datos/thdora.json
- Load data on instantiation, create file if not exists
- Accept filepath param for testability (tmp_path in tests)
- Implement all abstract methods including delete_appointment
- Add persistence tests: save → reload → verify
- Add .gitignore test to verify datos/ is excluded"

git push origin feat/json-lifemanager
# Abrir PR: feat/json-lifemanager → main
```

### TAREA 4 (esperar a que T3 esté mergeado)

```bash
git checkout main && git pull
git checkout -b feat/fastapi-endpoints

mkdir -p src/api/models src/api/routers
touch src/api/models/__init__.py src/api/routers/__init__.py

cp appointment.py         src/api/models/appointment.py
cp habit.py               src/api/models/habit.py
cp appointments_router.py src/api/routers/appointments.py
cp habits_router.py       src/api/routers/habits.py
cp main.py                src/api/main.py
cp test_api.py            tests/integration/test_api.py

pytest tests/ -v
# ✅ Todos deben pasar

git add src/api/
git add tests/integration/test_api.py
git commit -m "feat: implement FastAPI REST endpoints (Fase 6)

- Add Pydantic models: AppointmentCreate/Response, HabitCreate/Response
- Add routers: POST/GET /appointments/{date}, DELETE /appointments/{date}/{index}
- Add routers: POST/GET /habits/{date}
- Wire JsonLifeManager via dependency_overrides for testability
- Add integration tests with TestClient covering all endpoints
- Bump version to 0.5.0"

git push origin feat/fastapi-endpoints
# Abrir PR: feat/fastapi-endpoints → main
```

---

## Notas importantes

**T2 — VALID_TYPES:** Los tipos válidos son exactamente `médica`, `personal`, `trabajo`, `otra`
(en minúsculas, con tilde). Los tests existentes que usaban `"Médico"` se actualizan a `"médica"`.

**T3 — import de validación:** `json_lifemanager.py` importa `VALID_TYPES` y `_TIME_RE`
desde `memory_lifemanager.py` para no duplicar lógica. Si en el futuro se mueven a un módulo
de validación propio, solo hay que cambiar el import.

**T4 — Dependency injection:** El patrón usado es `app.dependency_overrides[JsonLifeManager]`.
En tests se sobreescribe con una instancia apuntando a `tmp_path` para aislar completamente
los tests del fichero real.

**T4 — `src/api/routers/__init__.py` y `src/api/models/__init__.py`:** Crear vacíos.
Son necesarios para que Python trate esas carpetas como paquetes.
```
