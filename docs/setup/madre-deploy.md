# Setup — Deploy THDORA en Madre

> Referencia técnica del entorno de producción en Madre (Omarchy).
> Última actualización: 14 junio 2026

---

## Máquina

| Campo | Valor |
|---|---|
| Nombre | Madre |
| OS | Omarchy — Arch Linux + Hyprland + Wayland |
| CPU | Intel i5-8400 |
| RAM | 16 GB |
| GPU | GTX 1060 6GB |
| IP Tailscale | `100.91.112.32` |
| Usuario | `varopc` |
| Path repo | `/home/varopc/dev/thdora` |

---

## Variables de entorno (`.env`)

```env
TELEGRAM_BOT_TOKEN=<token del bot>
GROQ_API_KEY=<key de console.groq.com>
```

> `THDORA_API_URL` NO va en `.env` — está definida en `docker-compose.yml` como `http://api:8000`.

---

## Comandos de gestión

```bash
# Arrancar
cd ~/dev/thdora
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Parar
docker compose down

# Reiniciar un servicio
docker compose restart bot

# Ver estado
docker compose ps

# Consola DB
docker compose exec api sqlite3 /app/data/thdora.db
```

---

## Notas del entorno

- Editor disponible: `nvim` (`nano` no instalado en Omarchy)
- Docker instalado y operativo
- Tailscale activo — acceso remoto desde Acer y MacBook vía `100.91.112.32`
- Red interna: bot → api vía nombre de servicio Docker (`http://api:8000`), no necesita IP pública
