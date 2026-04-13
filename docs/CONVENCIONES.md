# 📐 THDORA — Convenciones del sistema

> Reglas, patrones y decisiones que afectan a todo el proyecto.
> Leer antes de tocar cualquier fichero.
>
> **Navegación:** [README](../README.md) · [ARCHITECTURE](ARCHITECTURE.md) · [FLUJOS_DETALLADOS](FLUJOS_DETALLADOS.md)

---

## Patrones de `callback_data`

Todos los botones inline de Telegram tienen un `callback_data` con un prefijo que identifica la acción. Prefijos en uso:

| Prefijo | Handler | Significado |
|---------|---------|-------------|
| `menu_home` | `cb_menu_home` | Volver al menú principal |
| `quick_config` | `cb_quick_config` | Abrir `/config` desde menú |
| `quick_nueva_{date}` | `habito_start_desde_boton` | Nueva cita desde menú/vista |
| `quick_habito_{date}` | `habito_start_desde_boton` | Nuevo hábito desde menú/vista |
| `citas_nav_{date}` | `cb_citas_nav` | Navegar entre días en vista citas |
| `habitos_nav_{date}` | `cb_habitos_nav` | Navegar entre días en vista hábitos |
| `semana_nav_{date}` | `cb_semana_nav` | Navegar entre semanas |
| `cita_detail_{date}_{index}` | `cb_cita_detail` | Ver detalle de una cita |
| `ad_{date}_{index}` | `cb_apt_delete` | Borrar cita (pide confirmación) |
| `adc_{date}_{index}` | `cb_apt_delete_confirm` | Confirmar borrado de cita |
| `ae_{date}_{index}` | `cb_hab_edit_start` | Editar cita (entry point ConvHandler) |
| `hd_{date}_{habit}` | `cb_hab_delete` | Borrar hábito (pide confirmación) |
| `hdc_{date}_{habit}` | `cb_hab_delete_confirm` | Confirmar borrado de hábito |
| `he_{date}_{habit}` | `cb_hab_edit_start` | Editar hábito (entry point ConvHandler) |
| `ha_{date}_{habit}` | `cb_hab_add` | Sumar a hábito existente |
| `hval_{valor}` | handlers hábitos | Valor rápido de hábito |
| `hval___otro` | handlers hábitos | "Otro" — pide texto libre |
| `hconf_overwrite` | `habito_conflict_response` | Sobreescribir en conflicto |
| `hconf_add` | `habito_conflict_response` | Sumar en conflicto |
| `hconf_cancel` | `habito_conflict_response` | Cancelar en conflicto |
| `cfgt_{tipo}` | `cfg_recv_type` | Tipo de hábito en /config |
| `cancel_action` | `cb_cancel_action` | Cancelar acción inline |
| `nueva_franja_{key}` | handlers citas | Franja horaria seleccionada |
| `nueva_hora_{HH:MM}` | handlers citas | Hora en punto seleccionada |
| `nueva_cuarto_{HH:MM}` | handlers citas | Cuarto de hora seleccionado |
| `nueva_conflict_{accion}` | handlers citas | Resolver conflicto de hora |

> **Regla:** nunca reutilizar un prefijo. Si dos handlers comparten prefijo el que esté registrado antes en `main.py` lo capturará todo.

---

## Variables de entorno

| Variable | Obligatoria | Default | Descripción |
|----------|------------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Sí | — | Token de @BotFather. Sin él el bot no arranca |
| `THDORA_API_URL` | No | `http://localhost:8000` | URL base de la API |
| `THDORA_DB_PATH` | No | `data/thdora.db` | Ruta del fichero SQLite |

```bash
# .env (nunca versionar con datos reales)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
THDORA_API_URL=http://localhost:8000
THDORA_DB_PATH=data/thdora.db
```

> ⚠️ Si `TELEGRAM_BOT_TOKEN` no está definido, el bot llama a `sys.exit(1)` inmediatamente.
> Si `THDORA_API_URL` no responde, el bot **arranca igualmente** con un warning.

---

## Base de datos `data/thdora.db`

- Se crea automáticamente al arrancar la API si no existe (`init_db()` en `src/db/base.py`)
- No está versionada en Git (`.gitignore`)
- `data/.gitkeep` asegura que la carpeta sí está en el repo
- **Si se borra:** se pierde todos los datos. La API la recrea vacía al arrancar
- **Backup manual:** copiar `data/thdora.db` a otro directorio
- En Docker: el volumen `./data:/app/data` persiste la DB entre reinicios del contenedor

---

## Fechas — formato y convenciones

| Contexto | Formato | Ejemplo |
|----------|---------|--------|
| API (todas las rutas) | `YYYY-MM-DD` | `2026-04-13` |
| DB (columna `date`) | `YYYY-MM-DD` (string) | `2026-04-13` |
| Bot → usuario | texto natural | `lunes 13 de abril` |
| Bot → botones nav | compacto | `lun 13 abr` |
| Entrada usuario | flexible | `hoy`, `mañana`, `27/03`, `lunes`… |

Toda entrada de fecha del usuario pasa siempre por `_parse_date_flex()` o `_parse_date_arg()` antes de usarse. Nunca se envía a la API sin normalizar.

---

## Horas — formato y convenciones

| Contexto | Formato | Ejemplo |
|----------|---------|--------|
| API | `HH:MM` | `10:30` |
| DB (columna `time`) | `HH:MM` | `10:30` |
| Entrada usuario (exacta) | `HH:MM` o `HH:MM` | `10:30`, `930` → `09:30` |
| Botones franjas | `HH:00` | `06:00`, `07:00`… |

---

## Numeración de estados ConversationHandler

Cada ConversationHandler usa un rango de enteros para sus estados, evitando colisiones:

| Handler | Rango | Estados |
|---------|-------|--------|
| `/habito` | 10–12 | `HABITO_NOMBRE=10`, `HABITO_VALUE=11`, `HABITO_CONFLICT=12` |
| `/nueva` | 20–29 | `NUEVA_DATE=20`… `NUEVA_NOTES=28` |
| Editar hábito | 30–31 | `EDIT_HAB_NOMBRE=30`, `EDIT_HAB_VALUE=31` |
| Editar cita | 50–54 | `EDIT_APT_*` |
| `/config` | 40–47 | `CFG_NOMBRE=40`… `NOTIF_OFFSETS=47` (futuro) |

> **Regla:** nunca solapar rangos entre handlers. Si dos estados tienen el mismo número en handlers distintos, `per_message=False` puede causar comportamiento inesperado.

---

## Orden de registro de handlers en `main.py`

El orden importa. `python-telegram-bot` evalúa los handlers en el orden en que se registraron:

```
1. ConversationHandlers  ← máxima prioridad
   (capturan callbacks y mensajes dentro de un flujo activo)

2. CallbackQueryHandlers globales
   (botones fuera de flujos: nav, borrar, detalle…)

3. MessageHandler texto libre
   (_route_free_text → acumulación rápida de hábitos)

4. CommandHandlers simples
   (/start, /citas, /habitos, /semana, /resumen, /cancelar)

5. error_handler
```

> ⚠️ **Error común:** registrar un `CallbackQueryHandler` global con patrón muy amplio (ej: `r".*"`) antes de los ConversationHandlers. Capturaría todos los callbacks y los flujos dejarían de funcionar.

---

## Gestión de errores

```python
# Excepción pública del cliente HTTP
class ApiError(Exception):
    status_code: int  # código HTTP (0 si es error de red)

# El bot SIEMPRE captura ApiError y muestra mensaje amigable
# Nunca propaga la excepción al usuario
# El error_handler de main.py captura cualquier excepción no controlada
# y la loggea sin crashear el bot
```

### Timeouts HTTP (ThdoraApiClient)

| Tipo | Valor | Razón |
|------|-------|-------|
| `connect` | 10s | La API puede tardar en arrancar |
| `read` | 30s | Queries lentas en SQLite con muchos datos |
| `write` | 10s | POSTs/PUTs son rápidos |
| `pool` | 5s | Tiempo máximo esperando conexión libre |
| health check | 5s | Arranque rápido del bot |

---

## Convenciones de commits

Formato: `tipo: descripción breve`

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `refactor:` | Reorganización sin cambio de comportamiento |
| `docs:` | Solo documentación |
| `test:` | Tests nuevos o modificados |
| `chore:` | Tareas de mantenimiento (deps, CI, config) |
| `style:` | Formato, espacios (sin cambio lógico) |

```bash
# Ejemplos reales del proyecto
git commit -m "feat: franjas horarias en /nueva"
git commit -m "fix: entry point ConversationHandler desde botón menú"
git commit -m "docs: ARCHITECTURE.md — descripción de cada módulo"
git commit -m "refactor: handlers.py monolítico → 9 módulos"
```

---

## Convenciones de nombrado

| Elemento | Convención | Ejemplo |
|----------|-----------|--------|
| Handlers comando | `cmd_{nombre}` | `cmd_start`, `cmd_citas` |
| Handlers callback | `cb_{nombre}` | `cb_citas_nav`, `cb_apt_delete` |
| Builders ConvHandler | `build_{nombre}_handler()` | `build_nueva_handler()` |
| Keyboards | `_kb_{nombre}()` | `_kb_start()`, `_kb_franjas()` |
| Utils privados | `_{nombre}()` | `_parse_date_flex()`, `_greeting()` |
| Estados ConvHandler | `MAYUSCULAS` | `NUEVA_DATE`, `HABITO_NOMBRE` |
| Constantes | `MAYUSCULAS` | `TIPOS_CITA`, `FRANJAS` |

---

_Última actualización: 13 abril 2026 — 21:20 CEST_
