# 🚀 Guía: Arrancar THDORA en una máquina nueva

> Guía basada en la experiencia real del 18 junio 2026.
> Sigue estos pasos **en orden** para evitar los 4 bugs documentados en esa sesión.

---

## Requisitos previos

- Docker + Docker Compose instalados
- Clave SSH configurada en GitHub (`ssh -T git@github.com` debe responder `Hi ...`)
- `.env` disponible (del clone anterior o configurado desde `.env.example`)

---

## Pasos

### 1. Clonar el repo

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone git@github.com:alvarofernandezmota-tech/thdora.git
cd thdora
pwd  # debe mostrar /home/varopc/Projects/thdora
```

### 2. Configurar el `.env`

**Opción A — tienes un `.env` anterior:**
```bash
cp ~/dev/thdora/.env ~/Projects/thdora/.env
# o desde otro equipo / backup
```

**Opción B — desde cero:**
```bash
cp .env.example .env
nvim .env  # rellenar TELEGRAM_BOT_TOKEN, GROQ_API_KEY, ALLOWED_USERS
```

> ⚠️ El `.env` **NUNCA** va al repo. Está en `.gitignore`.
> El `docker compose` busca `.env` en la misma carpeta donde se ejecuta.

### 3. Levantar el stack

```bash
docker compose up -d --build
```

Eso levanta API + Bot en una sola operación con rebuild de imagen.

### 4. Verificar que todo funciona

```bash
docker ps                        # ver contenedores corriendo
docker compose logs -f bot       # logs del bot en tiempo real
docker compose logs -f thdora    # logs de la API
curl http://localhost:8000/health/live  # debe devolver 200
```

### 5. Si necesitas solo el bot

```bash
docker compose up -d --build bot
docker compose logs -f bot
```

---

## Comandos útiles de mantenimiento

```bash
# Rebuild limpio (si hay cambios en deps o Dockerfile)
docker compose down
docker compose build --no-cache
docker compose up -d

# Actualizar desde main
git pull origin main
docker compose build bot    # solo si cambiaron deps
docker compose up -d bot

# Ver estado
docker compose ps
docker compose logs --tail=50 bot

# Reiniciar solo el bot
docker compose restart bot
```

---

## Errores frecuentes y su solución

| Error | Causa | Solución |
|-------|-------|----------|
| `fatal: not a git repository` | No estás en `~/Projects/thdora` | `cd ~/Projects/thdora` |
| `env file .env not found` | Falta `.env` en la carpeta | `cp .env.example .env` |
| `ImportError: cannot import name X` | Imagen Docker desactualizada | `docker compose build bot` |
| `ModuleNotFoundError: No module named X` | Paquete no en `requirements.txt` | Añadir paquete + `docker compose build` |
| `attempt to write a readonly database` | UID mismatch en `./data` | `sudo chown -R 1000:1000 ./data ./logs` |
| `executable file not found: curl` | `curl` no está en imagen slim | Usar `python3 -c "import urllib..."` en healthcheck |

---

## Ver también

- [`scripts/deploy.sh`](../../scripts/deploy.sh) — script de deploy reproducible
- [`docs/sesiones/2026-06-18-docker-nueva-maquina.md`](../sesiones/2026-06-18-docker-nueva-maquina.md) — sesión completa con todos los detalles
- [`CHANGELOG.md`](../../CHANGELOG.md) — historial de versiones
