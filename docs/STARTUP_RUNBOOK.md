# THDORA — Runbook de Arranque

> Guía definitiva para levantar THDORA desde cero o tras un pull.
> Última actualización: 18 junio 2026

---

## Requisitos Previos

- Docker + Docker Compose v2 instalados
- `.env` configurado con tokens reales (ver `.env.example`)
- Puerto 8000, 9090 y 3000 libres
- Carpeta `./data` con permisos `1000:1000`

```bash
# Verificar permisos de data/
ls -la data/
# Si no existe o los permisos son incorrectos:
mkdir -p data logs
chown -R 1000:1000 data logs
```

---

## Arranque Estándar (tras git pull)

```bash
cd ~/Projects/thdora
git pull origin main

# 1. Smoke test (verifica imports, config, DB, agente — ~2 min)
make smoke

# 2. Si smoke pasa → build limpio y arranque
make fresh

# 3. Ver logs en tiempo real
make logs
```

---

## Primer Arranque desde Cero

```bash
cd ~/Projects/thdora
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# Configurar entorno
cp .env.example .env
# ← EDITAR .env con tokens reales antes de continuar

# Crear carpetas con permisos correctos
mkdir -p data logs
chown -R 1000:1000 data logs

# Smoke test
make smoke

# Arranque
make fresh
make logs
```

---

## Verificación Manual Post-Arranque

Una vez que los logs muestran `🤖 Iniciando THDORA Bot...`, prueba en Telegram:

| Mensaje | Respuesta esperada |
|---------|-------------------|
| `/start` | Menú principal con botones |
| `hola` | Respuesta del agente Groq |
| `mañana tengo dentista a las 10` | ⚠️ Responde texto pero no crea cita aún (BUG-002) |
| `/nueva` | Flujo interactivo para crear cita ✅ |
| `/citas` | Lista de citas del día |
| `/habitos` | Lista de hábitos |

---

## Comandos Makefile Disponibles

```bash
make up           # Arranca con rebuild si hay cambios
make fresh        # Down + build sin cache + up
make smoke        # Smoke test completo (22 checks)
make logs         # Logs del bot en tiempo real
make logs-api     # Logs de la API
make ps           # Estado de contenedores
make shell-bot    # Bash dentro del bot
make shell-api    # Bash dentro de la API
make pull         # git pull + restart bot
make start-fresh  # Todo de una: pull → smoke → fresh → logs
make rebuild      # Build sin cache
make down         # Para todos los servicios
```

---

## Diagnóstico de Fallos Comunes

### Bot no arranca / timeout esperando API
```bash
# Ver logs de la API
make logs-api
# Verificar healthcheck
docker inspect thdora | grep -A 10 Health
```

### Error de permisos en data/
```bash
chown -R 1000:1000 ./data ./logs
docker compose restart thdora
```

### Prometheus falla al arrancar
```bash
# Verificar que monitoring/prometheus/prometheus.yml existe
ls monitoring/prometheus/
# Si falta:
mkdir -p monitoring/prometheus
# Ver docs/THDORA_AUDIT_2026-06-18.md → BUG-003
```

### Import error en el bot
```bash
# Ejecutar smoke test para ver qué falla
make smoke
# O entrar al contenedor
make shell-bot
python -c "from src.config import settings; print(settings)"
```

### Duplicated timeseries en Prometheus
```bash
# Ya está corregido en metrics.py con _safe_* helpers
# Si persiste, reiniciar contenedores
make down && make up
```

---

## Auditoría IA (opcional pero recomendado)

```bash
# Con Claude:
ANTHROPIC_API_KEY=tu_clave python scripts/ai_audit.py

# Con Grok/xAI:
GROK_API_KEY=tu_clave python scripts/ai_audit.py

# El reporte se guarda en audit_report.md
# Pegar el contenido en Perplexity para aplicar fixes al repo
```

---

## URLs de Servicios (local)

| Servicio | URL |
|----------|-----|
| API FastAPI | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health/live |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |
