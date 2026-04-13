# 📍 THDORA — CÓMO PROCEDER

> Este fichero es tu punto de entrada **cada vez que abres el proyecto**.
> Te dice exactamente dónde estás, qué tienes que hacer ahora y en qué orden.
>
> **Navegación:** [README](README.md) · [ROADMAP](ROADMAP.md) · [CHANGELOG](CHANGELOG.md) · [Índice docs](docs/INDEX.md)

---

## 📍 Dónde estamos ahora — v0.11.0 (13 abril 2026)

```
✅ F9.3  — UI unificada (menú inline, navegación, cambio de vista)
✅ F9.4  — Vista detalle de cita con click en ⏰ hora
✅ F9.5  — UX avanzada: saludo contextual, fechas flexibles, franjas horarias
✅ F9.6  — Refactor: handlers.py monolítico → 9 módulos limpios
✅ F9.7  — Docker + despliegue 24/7
✅ TEST  — Pruebas en vivo completadas (13 abril 2026) — todo funciona
✅ FIX   — Entry points ConversationHandlers arreglados (botones menú funcionan)
🔜 NEXT  — F10 Docker 24/7 o F11 Multi-usuario o F12 Notificaciones
```

---

## ⏰ Arranque rápido (modo local)

### Requisitos previos
- Python 3.12 instalado
- Entorno virtual activo: `pip install -e ".[dev]"` o simplemente `make dev`
- Fichero `.env` en la raíz:

```bash
# .env
TELEGRAM_BOT_TOKEN=tu_token_aqui
THDORA_API_URL=http://localhost:8000
THDORA_DB_PATH=data/thdora.db
```

### Pasos para arrancar

```bash
# Matar procesos que puedan quedar de sesiones anteriores
fuser -k 8000/tcp
pkill -9 -f "bot.main"
sleep 2

# Terminal 1 — API
make run-api
# Verifica: http://localhost:8000/health → {"status": "ok"}

# Terminal 2 — Bot
python3 -m src.bot.main
# Debería mostrar: "🤖 THDORA bot v3.2 arrancando (polling)…"
```

> ⚠️ Si ves `Conflict: terminated by other getUpdates` es porque hay **otra instancia del bot corriendo**.
> Solución: `pkill -9 -f "bot.main"` y volver a arrancar.

### Arranque con Docker (alternativa)

```bash
cp docker/.env.docker.example .env
# edita .env y pon tu TELEGRAM_BOT_TOKEN real

make docker-build    # construye la imagen (~2 min primera vez)
make docker-up       # arranca api + bot en segundo plano
make docker-logs     # ver logs en vivo
make docker-down     # parar todo
```

---

## 🧪 Pruebas automáticas

```bash
make test          # todos los tests
make test-bot      # solo tests del bot (sin API ni Telegram real)
make test-cov      # con cobertura → htmlcov/index.html
```

---

## ✅ Estado de pruebas en vivo (13 abril 2026)

Todas las funciones probadas en Telegram real. Resultados:

| Función | Estado | Notas |
|---------|--------|-------|
| `/start` + menú inline | ✅ | |
| ➕ Nueva cita desde botón menú | ✅ | Fix entry point aplicado |
| Flujo franjas horarias `/nueva` | ✅ | |
| Crear cita → API `POST /appointments/` | ✅ | 201 Created |
| Borrar cita → API `DELETE /appointments/` | ✅ | 204 No Content |
| Editar cita | ✅ | |
| Navegación ◀️▶️ citas/hábitos | ✅ | |
| ➕ Nuevo hábito desde botón menú | ✅ | Fix entry point aplicado |
| Registrar hábito → API `POST /habits/` | ✅ | 201 Created |
| Editar/sumar hábito | ✅ | |
| `/semana` | ✅ | |

---

## 💡 Cómo trabajamos en este proyecto

> Contexto para retomar el trabajo rápidamente en cualquier sesión.

### Flujo de sesión típico
1. **Leer este fichero** — saber dónde estamos
2. **Arrancar API + Bot** — comandos de arriba
3. **Trabajar en la feature** — editar código, probar en Telegram
4. **Pushear** — commits semánticos, actualizar ROADMAP + CHANGELOG
5. **Actualizar este fichero** — reflejar el nuevo estado

### Convenciones de código
- **Handlers**: cada dominio tiene su módulo (`citas.py`, `habitos.py`, etc.)
- **Entry points**: los `ConversationHandler` se construyen con `build_*_handler()` y se registran en `main.py`
- **Callbacks del menú**: los botones `quick_nueva_*` y `quick_habito_*` son capturados como entry points de sus respectivos `ConversationHandler`, NO por un dispatcher central
- **Keyboards**: todos en `keyboards.py`, nunca inline en los handlers
- **API calls**: siempre a través de `ThdoraApiClient` en `api_client.py`
- **Fechas**: siempre pasar por `_parse_date_flex` o `_parse_date_arg` de `utils/dates.py`

### Estructura de estados ConversationHandler
```
/nueva (citas):
  NUEVA_DATE → NUEVA_FRANJA → NUEVA_HORA_PUNTO → NUEVA_HORA_CUARTO
  → NUEVA_TIME (si exacta) → NUEVA_CONFLICT (si hay conflicto)
  → NUEVA_NOMBRE → NUEVA_TYPE → NUEVA_NOTES → END

/habito (hábitos):
  HABITO_NOMBRE → HABITO_VALUE → HABITO_CONFLICT (si existe) → END

Editar cita:
  EDIT_APT_TIME → EDIT_APT_NOMBRE → EDIT_APT_TYPE → EDIT_APT_NOTES → END

Editar hábito:
  EDIT_HAB_NOMBRE → EDIT_HAB_VALUE → END

Config:
  CFG_NOMBRE → CFG_TYPE → CFG_UNIT → CFG_QUICK → END
```

---

## 🔜 Siguiente — opciones para v0.12.x

Cualquiera de estas tres se puede hacer en la próxima sesión:

### Opción A — F10 Docker + despliegue 24/7
> El bot corre siempre en un servidor, sin intervención manual.
- `Dockerfile` + `docker-compose.yml` multi-servicio
- Health checks y reinicio automático
- Probar en VPS (Railway / DigitalOcean / Raspberry Pi)

### Opción B — F12 Notificaciones proactivas
> El bot avisa sin que el usuario pregunte.
- APScheduler integrado en `src/bot/scheduler.py`
- Morning check-in (08:00): citas del día
- Alerta −30 min antes de una cita
- Evening log (22:00): registra hábitos del día

### Opción C — F13 IA conversacional
> Hablar con el bot en lenguaje natural.
- Provider abstracto (Groq / OpenAI / Ollama)
- `intent_parser.py` — extrae intención + entidades
- `/ia` modo conversación libre
- Soporte voz con Whisper

---

## 📄 F11 Multi-usuario (cuando toque)

### Cambios en SQLite
```python
# src/db/models.py — añadir en Appointment y Habit:
user_id = Column(String, nullable=False, index=True)
```

### Cambios en la API
```python
# Header X-User-Id en todos los endpoints
# Todos los queries filtran por user_id
```

### Cambios en el bot
```python
# api_client.py pasa user_id en cada llamada:
# update.effective_user.id  → Telegram siempre lo tiene
```

---

_Última actualización: 13 abril 2026 — 20:45 CEST_
