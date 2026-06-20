# 🚀 THDORA — Plan de Deploy (Servidor Madre)
_Actualizado: 2026-06-20 — v0.17.0 listo en main_

## ⚡ Estado actual
- **main**: v0.17.0 completo — todos los bugs B12-B25 corregidos
- **Tests**: suite completa en `tests/` (pytest-asyncio + AsyncMock)
- **CI**: GitHub Actions configurado (lint + tests en cada push)
- **Docker**: stack corregido — `docker-compose.yml` + `Dockerfile` + `entrypoint.sh`

---

## 🔧 Checklist de deploy en Servidor Madre

### 1. Antes de arrancar (una sola vez)
```bash
# En el servidor, en el directorio del proyecto
git pull origin main

# Verificar que .env existe y tiene todas las variables
cp .env.example .env
# Editar con los valores reales:
#   TELEGRAM_TOKEN=...
#   GROQ_API_KEY=...
#   SECRET_KEY=...
#   DATABASE_URL=sqlite:///./data/thdora.db
#   ALLOWED_USER_ID=tu_telegram_id
#   THDORA_API_URL=http://thdora:8000  (Docker interno)
```

### 2. Verificar ecosistema antes de construir
```bash
python scripts/autotest.py --fast
```
Debe mostrar `✅` en todos los checks.

### 3. Construir y arrancar
```bash
# Construir imágenes frescas
docker compose build --no-cache

# Arrancar todo
docker compose up -d

# Verificar que los servicios están healthy
docker compose ps
```

Esperar ~30s a que la API pase a `healthy`. El bot NO arranca hasta que la API esté healthy.

### 4. Verificar logs
```bash
# Logs API (debe mostrar alembic + uvicorn OK)
docker compose logs -f thdora

# Logs Bot (debe mostrar PTB polling OK)
docker compose logs -f bot
```

### 5. Smoke test manual
- Abrir Telegram → enviar `/start` al bot
- Enviar `/citas` → debe mostrar citas del día
- Enviar `/habitos` → debe mostrar hábitos
- Enviar texto libre → debe responder vía NLP

---

## 🔐 Secrets necesarios en GitHub Actions
Para que el CI funcione completamente:
- `TELEGRAM_TOKEN` — token del bot
- `GROQ_API_KEY` — API key de Groq
- `SECRET_KEY` — clave secreta de la app
- `ALLOWED_USER_ID` — tu Telegram ID

Añadirlos en: `GitHub repo → Settings → Secrets and variables → Actions`

---

## 📋 Flujo de servicios Docker
```
prometheus (independiente)
    ↓
grafana (depends_on: prometheus)

thdora/API (independiente, healthcheck en /health/live)
    ↓ [espera: service_healthy]
bot (arranca solo cuando API está healthy)
```

## ⚠️ Notas importantes
- `SERVICE_TARGET=api` en el servicio `thdora`
- `SERVICE_TARGET=bot` en el servicio `bot`
- `THDORA_API_URL=http://thdora:8000` en el bot (red interna Docker)
- El bot **nunca** accede a la BD directamente, solo vía HTTP a la API
- `alembic upgrade head` se ejecuta automáticamente al arrancar la API
- Si hay error en alembic, la API no arranca y el bot espera → fácil de detectar en logs

---

## 🐛 Si algo falla
```bash
# Ver todos los logs
docker compose logs

# Reiniciar solo la API
docker compose restart thdora

# Reiniciar solo el bot
docker compose restart bot

# Parar todo y limpiar
docker compose down

# Reconstruir desde cero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```
