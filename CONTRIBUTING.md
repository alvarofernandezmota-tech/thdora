# Contribuir a THDORA

## Configuración del entorno de desarrollo

```bash
# 1. Clonar
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt
pip install ruff pytest pytest-asyncio pytest-cov

# 4. Variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Verificar que todo esté bien
python scripts/autotest.py --fast
pytest tests/ -v
```

## Flujo de trabajo Git

```
main           ← solo merges de PR, requiere CI verde
  └─ develop    ← integración continua
       └─ feature/nombre-corto   ← desarrollo
       └─ fix/nombre-del-bug     ← correcciones
```

### Commits — Conventional Commits

```
feat(habitos): añadir vista semanal de hábitos
fix(citas): corregir user_id en delete_appointment
test(config): tests para toggle de notificaciones
chore(ci): añadir step de smoke test Docker
docs(arch): actualizar diagrama de capas
refactor(api_client): extraer _validate_user_id
```

Formato: `tipo(scope): descripción en minúsculas, tiempo presente`

## Añadir un nuevo handler

1. Crear `src/bot/handlers/mi_handler.py` con:
   - La lógica en funciones `async def`
   - Una factory `def build_mi_handler() -> ConversationHandler`
   - Import de `ThdoraApiClient` como `api = ThdoraApiClient()` (singleton, no instanciar en cada función)

2. Exportar en `src/bot/handlers/__init__.py`

3. Registrar en `src/bot/main.py` dentro de `build_app()`

4. Crear `tests/test_mi_handler.py` con al menos:
   - Test del entry point (devuelve el estado correcto)
   - Test del happy path completo
   - Test de error (ApiError capturado correctamente)

5. Actualizar `CHANGELOG.md` con la versión siguiente

## Añadir un endpoint a la API

1. Crear/modificar router en `src/api/routers/`
2. Registrar en `src/api/main.py`
3. Si cambia el schema, crear migración: `alembic revision --autogenerate -m "descripcion"`
4. Añadir método a `ThdoraApiClient` en `src/bot/api_client.py`
5. Test unitario en `tests/test_api_client.py`

## Reglas de código

- **Linter**: `ruff check src/ tests/` debe pasar sin errores
- **Formato**: `ruff format src/ tests/` (o `ruff format --check` en CI)
- **Type hints**: obligatorios en firmas públicas de `api_client.py`; recomendados en el resto
- **user_id**: SIEMPRE pasarlo explícitamente. Nunca leerlo de estado global
- **Logging**: usar `logger = logging.getLogger(__name__)` en cada módulo, no `print()`
- **Errores de API**: capturar `ApiError` en el handler, nunca dejar propagar a PTB

## Checklist antes de hacer PR

- [ ] `python scripts/autotest.py --fast` pasa al 100%
- [ ] `pytest tests/ -v` pasa sin errores
- [ ] `ruff check src/ tests/` sin errores
- [ ] `CHANGELOG.md` actualizado
- [ ] Si cambia una firma de `ThdoraApiClient`, actualizar todos los handlers que la usan
- [ ] Si se añade un handler nuevo, registrado en `main.py` y exportado en `__init__.py`
