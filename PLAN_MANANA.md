# 📋 PLAN DE LANZAMIENTO — THDORA v0.17
_Actualizado: 2026-06-20 01:20 CEST_

## Estado actual del código

✅ Todos los bugs B12-B25 corregidos y subidos a `main`  
✅ `habitos.py` completo (ya no truncado)  
✅ `citas.py` con `_find_overlap()` local (sin dependencia de endpoint inexistente)  
✅ `config.py` con todas las firmas de API correctas  
✅ `Dockerfile` multi-stage con entrypoint diferenciado  
✅ `docker/entrypoint.sh` con `alembic upgrade head` antes de uvicorn  
✅ `CHANGELOG.md` actualizado a v0.17  

## Pasos para lanzar mañana

### 0. Pre-requisitos (5 min)

```bash
# Clonar o hacer pull de main
git pull origin main

# Crear .env desde el ejemplo
cp .env.example .env
```

Editar `.env` y rellenar:
```
TELEGRAM_TOKEN=tu_token_del_botfather
DATABASE_URL=sqlite:///./data/thdora.db
OPENAI_API_KEY=sk-...          # opcional para MVP
ALLOWED_USER_ID=tu_telegram_id  # /me en @userinfobot
SECRET_KEY=cualquier_string_aleatorio_32chars
```

### 1. Build y arranque (3 min)

```bash
docker compose up --build
```

Esperar a ver en logs:
- `✅ Migraciones aplicadas` (servicio thdora/api)
- `🌐 Arrancando FastAPI...`
- Bot log: `Bot iniciado. Esperando mensajes...`

### 2. Verificación rápida (2 min)

En Telegram con tu bot:
```
/start          → debe responder con menú
/habito         → flujo 2 pasos, registra un hábito
/habitos        → lista hábitos de hoy
/nueva          → flujo cita completo (6 pasos)
/citas          → lista citas de hoy
/config         → menú configuración
```

### 3. Si algo falla

```bash
# Ver logs en tiempo real
docker compose logs -f thdora
docker compose logs -f bot

# Reiniciar solo el bot (sin reconstruir)
docker compose restart bot

# Acceder a la BD directamente
docker compose exec thdora sqlite3 /app/data/thdora.db ".tables"
```

### 4. Errores conocidos posibles

| Error | Causa | Solución |
|-------|-------|----------|
| `TELEGRAM_TOKEN env var missing` | .env no creado | `cp .env.example .env` |
| `No module named src` | PYTHONPATH mal | Ya en Dockerfile: `ENV PYTHONPATH=/app` |
| `alembic: command not found` | imagen vieja | `docker compose build --no-cache` |
| `sqlite3.OperationalError: no such table` | migración no corrió | Ver logs del entrypoint |
| `Conflict: terminated by other getUpdates` | bot ya corriendo | Parar otro proceso del bot |

## Roadmap post-lanzamiento (features 1 a 1)

### Semana 1 — Estabilidad
- [ ] Tests unitarios para `ThdoraApiClient` (mocks de httpx)
- [ ] Tests de integración para los 3 ConversationHandlers principales
- [ ] CI con GitHub Actions: lint + tests en cada PR

### Semana 2 — UX
- [ ] Comando `/hoy` — resumen del día (citas + hábitos) en un solo mensaje
- [ ] Comando `/semana` — vista semanal
- [ ] Menú principal mejorado con botones rápidos

### Semana 3 — Notifications
- [ ] Scheduler: reminder de citas X minutos antes
- [ ] Resumen diario automático a la hora configurada
- [ ] Evening log automático

### Semana 4 — Inteligencia
- [ ] NLP: registrar hábito en lenguaje natural (`"dormi 8 horas"`)
- [ ] `/ia` o `/chat` — integrar OpenAI para consultas sobre tus datos

## Nota para Claude / LLM siguiente sesión

Leer en orden antes de tocar código:
1. `CONTEXT.md` — arquitectura general y decisiones de diseño
2. `CHANGELOG.md` — estado real del código y bugs ya corregidos
3. `llms.txt` — resumen compacto para LLMs
4. Este `PLAN_MANANA.md` — estado del lanzamiento

Versón actual: **v0.17.0**  
Branch activo: **main**  
Próxima tarea: tests + comando `/hoy`
