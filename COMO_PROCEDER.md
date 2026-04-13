# 🧭 THDORA — Cómo proceder

> Guía de trabajo para retomar el proyecto después de un descanso.
> Estado al día, siguiente paso claro, sin buscar contexto.
>
> **Navegación:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## 📍 Estado actual — 13 abril 2026

**Versión:** v0.11.0
**Todo el bot probado en vivo y funcionando al 100%.**
**Documentación técnica completa** — flujos, API, convenciones, diseño F12.

### ✅ Funciona hoy
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- CRUD completo de citas y hábitos con SQLite
- Franjas horarias en `/nueva`
- Conflicto de hora y conflicto de hábito gestionados
- `/config` configura tipos y botones rápidos de hábitos
- Menú operativo con botones de acceso rápido

### ❌ No implementado todavía
- **Notificaciones proactivas** (F12) ← siguiente
- **Docker / despliegue 24/7** (F10)
- **Multi-usuario** (F11)
- **IA conversacional** (F13)
- **Tracking personal** (F14)
- **Gamificación** (F15)

---

## ⏭️ Siguiente paso — F12 Notificaciones

El diseño está **completamente cerrado** en [`docs/F12_NOTIFICACIONES_DESIGN.md`](docs/F12_NOTIFICACIONES_DESIGN.md).
No hay nada que decidir. Solo implementar en este orden:

```
1. src/db/models.py              ← + tabla UserConfig
2. src/core/impl/sqlite_lifemanager.py  ← get_user_config / upsert
3. src/api/routers/user_config.py       ← GET + PUT /user_config/{user_id}
4. src/api/main.py               ← registrar router
5. src/bot/api_client.py         ← get_user_config / update_user_config
6. src/bot/keyboards.py          ← _kb_config_menu, _kb_notif_menu, _kb_notif_hora, _kb_notif_offsets
7. src/bot/handlers/config.py    ← CFG_MENU raíz + rama notificaciones
8. src/bot/scheduler.py          ← APScheduler: resumen diario + evening log + jobs cita
9. src/bot/handlers/citas.py     ← reprogramar jobs al crear/editar/borrar
10. src/bot/main.py              ← start_scheduler(app)
```

---

## 🛠️ Cómo arrancar el proyecto

```bash
# 1. Clonar y entrar
git clone https://github.com/alvarofernandezmota-tech/thdora
cd thdora

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env
# Editar .env: poner TELEGRAM_BOT_TOKEN

# 4. Arrancar API + Bot en terminales separadas
make run-api    # → http://localhost:8000
make run-bot    # → bot escuchando en Telegram

# Alternativa Docker (cuando F10 esté listo)
# docker-compose up
```

---

## 📁 Estructura del proyecto

```
thdora/
├── src/
│   ├── core/              ← lógica de negocio pura
│   │   ├── abstract/      ← AbstractLifeManager
│   │   └── impl/          ← SQLiteLifeManager
│   ├── db/
│   │   ├── models.py      ← tablas SQLAlchemy
│   │   └── base.py        ← init_db()
│   ├── api/
│   │   ├── main.py        ← FastAPI app
│   │   └── routers/       ← appointments, habits, habit_config, summary
│   └── bot/
│       ├── main.py        ← entrypoint bot
│       ├── api_client.py  ← cliente HTTP async
│       ├── keyboards.py   ← todos los teclados inline
│       ├── utils/
│       │   ├── dates.py   ← parse fechas flexibles
│       │   └── accum.py   ← lógica acumulación +N
│       └── handlers/
│           ├── menu.py    ← /start, menú principal
│           ├── citas.py   ← /citas, /nueva, editar, borrar
│           ├── habitos.py ← /habitos, /habito, editar, sumar
│           ├── semana.py  ← /semana
│           ├── config.py  ← /config (se rediseña en F12)
│           └── common.py  ← /cancelar, error_handler
├── data/
│   └── thdora.db          ← SQLite (no versionado)
├── docs/                  ← documentación técnica completa
├── Makefile
├── requirements.txt
└── .env.example
```

---

## 📖 Documentación disponible

| Doc | Para qué sirve |
|-----|---------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Estructura y decisiones de diseño |
| [docs/FLUJOS_DETALLADOS.md](docs/FLUJOS_DETALLADOS.md) | Estados, transiciones, casos borde de todos los flujos |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Todos los endpoints con ejemplos |
| [docs/CONVENCIONES.md](docs/CONVENCIONES.md) | Patrones callback_data, variables entorno, orden handlers |
| [docs/F12_NOTIFICACIONES_DESIGN.md](docs/F12_NOTIFICACIONES_DESIGN.md) | Diseño completo de la siguiente feature |
| [docs/INDEX.md](docs/INDEX.md) | Mapa completo de toda la documentación |

---

## 📅 Convenciones rápidas

```bash
# Commits
git commit -m "feat: descripción"
git commit -m "fix: descripción"
git commit -m "docs: descripción"
git commit -m "refactor: descripción"

# Prefijos callback_data (resumen)
ad_  adc_   → borrar/confirmar cita
ae_          → editar cita
hd_  hdc_   → borrar/confirmar hábito
he_          → editar hábito
ha_          → sumar a hábito
hval_        → valor rápido hábito
hconf_       → resolver conflicto hábito
# Lista completa → docs/CONVENCIONES.md
```

---

_Última actualización: 13 abril 2026 — 21:24 CEST_
