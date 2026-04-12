# 📍 THDORA — CÓMO PROCEDER

> Este fichero es tu punto de entrada cada vez que abres el proyecto.  
> Te dice exactamente dónde estás, qué tienes que hacer ahora y en qué orden.
>
> **Navegación:** [README](README.md) · [ROADMAP](ROADMAP.md) · [CHANGELOG](CHANGELOG.md) · [Índice docs](docs/INDEX.md)

---

## 📍 Dónde estamos ahora — v0.11.0 (12 abril 2026)

```
✅ F9.6  — handlers.py monolítico → 9 módulos limpios
✅ F9.7  — Docker + despliegue 24/7
✅ Tests — 72 casos nuevos para el bot (unit + handlers)
⚠️  PENDIENTE — prueba en vivo de F9.3 → F9.7 (nunca probado en Telegram real)
🔒  BLOQUEADO — F9.8 Multi-usuario (no empezar hasta que el checklist esté limpio)
```

---

## ⏰ Arranque rápido (modo local)

### Requisitos previos
- Python 3.12 instalado
- Entorno virtual activo con `pip install -e ".[dev]"`  
  (o simplemente `make dev`)
- Fichero `.env` en la raíz con tu token real:

```bash
# .env
TELEGRAM_BOT_TOKEN=tu_token_aqui
THDORA_API_URL=http://localhost:8000
THDORA_DB_PATH=data/thdora.db
```

### Pasos para arrancar

```bash
# Terminal 1 — API
make run-api
# Debería responder en http://localhost:8000
# Verifica: http://localhost:8000/health  → {"status": "ok"}

# Terminal 2 — Bot
make run-bot
# Debería mostrar: "Bot arrancado. Esperando mensajes..."
```

### Arranque con Docker (alternativa)

```bash
# Primera vez
cp docker/.env.docker.example .env
# edita .env y pon tu TELEGRAM_BOT_TOKEN real

make docker-build    # construye la imagen (~2 min primera vez)
make docker-up       # arranca api + bot en segundo plano
make docker-logs     # ver logs en vivo
make docker-down     # parar todo
```

---

## 🧪 Pruebas automáticas (sin Telegram)

```bash
# Todos los tests
make test

# Solo tests del bot (los nuevos de esta sesión)
make test-bot

# Con cobertura
make test-cov
# Abre htmlcov/index.html para ver el informe
```

> Los tests del bot usan mocks — no necesitas la API ni el bot arrancados.

---

## ✅ Checklist de prueba en vivo

> Ejecuta esto con la API y el bot arrancados. Marca cada casilla en tu Telegram.
> Si algo falla, anota el bug en `docs/diarios/FECHA.md` y corriges antes de seguir.

### 🟢 Bloque 1 — Menú principal
- [ ] `/start` → aparece menú con botones inline
- [ ] El saludo cambia según la hora (🌅 mañana / 🌆 tarde / 🌙 noche)
- [ ] Botón `📅 Citas de hoy` → abre vista citas
- [ ] Botón `💪 Hábitos de hoy` → abre vista hábitos
- [ ] Botón `➕ Nueva cita` desde menú → arranca flujo /nueva
- [ ] `/cancelar` en mitad de cualquier flujo → cancela limpiamente

### 🟢 Bloque 2 — Citas: navegación
- [ ] `/citas` → muestra citas de hoy
- [ ] Botón `◀️` → día anterior
- [ ] Botón `▶️` → día siguiente
- [ ] Botón central (fecha) → muestra la fecha real
- [ ] Botón `🏠 Menú` → vuelve al menú principal
- [ ] Botón `📋 Semana` → abre vista semanal
- [ ] Botón `💤 Hábitos` → cambia a vista hábitos del mismo día

### 🟢 Bloque 3 — /nueva con franjas horarias
- [ ] `➕ Nueva` desde vista citas → pide fecha
- [ ] Fecha `hoy` → avanza a franjas
- [ ] Fecha `mañana` → avanza a franjas
- [ ] Fecha inválida (ej. `zzz`) → pide de nuevo (no cuelga)
- [ ] Botón `🌅 Mañana` → muestra botones 06:00–13:00
- [ ] Botón `🌆 Tarde` → muestra botones 14:00–21:00
- [ ] Botón `🌙 Noche` → muestra botones 22:00–05:00
- [ ] Botón `✏️ Exacta` en franjas → pide HH:MM directamente
- [ ] Seleccionar hora en punto (ej. 10:00) → muestra cuartos
- [ ] Botón `🕐 Ver cuartos` → muestra cuartos
- [ ] Seleccionar cuarto (ej. 10:30) → pide nombre
- [ ] Botón `✏️ Exacta` en hora/cuarto → pide HH:MM
- [ ] HH:MM válida (10:30) → pide nombre
- [ ] HH:MM inválida (99:99) → pide de nuevo
- [ ] Nombre → tipo → notas (o `/skip`) → cita guardada
- [ ] Conflicto de hora → aviso ⚠️ + vuelve a franjas (no a texto)
- [ ] Cita guardada aparece en `/citas` del día correspondiente

### 🟢 Bloque 4 — Citas: detalle y acciones
- [ ] Click en ⏰ hora de una cita → abre vista detalle
- [ ] Vista detalle muestra: fecha, hora, nombre, tipo, notas
- [ ] Botón `Editar` → flujo de edición funciona
- [ ] Botón `Borrar` → pide confirmación → se borra → desaparece de la lista
- [ ] Botón `← Volver` → regresa a la vista del día

### 🟢 Bloque 5 — Hábitos
- [ ] `/habitos` → muestra hábitos de hoy
- [ ] Navegación ◀️▶️ igual que en citas
- [ ] Botón `📊 Citas` → cambia a vista citas del mismo día
- [ ] `➕ Nuevo` desde vista hábitos → pide nombre libre
- [ ] `/habito` → nombre libre → valor → guardado en DB
- [ ] Valor `+N` sobre hábito existente → acumula (ej. 1L + 0.5L = 1.5L)
- [ ] Valor sin `+` sobre existente → conflicto: Sobreescribir / Sumar / Cancelar
- [ ] Editar nombre del hábito → se actualiza
- [ ] Editar valor del hábito → se actualiza
- [ ] Borrar hábito → desaparece de la lista
- [ ] Botón `➕` en hábito existente (sumar rápido) → pide valor

### 🟢 Bloque 6 — Semana y Config
- [ ] `/semana` → muestra semana actual con hábitos/citas por día
- [ ] Nav ◀️▶️ entre semanas
- [ ] Click en un día de la semana → abre vista citas de ese día
- [ ] `/config` → muestra configuración de hábitos
- [ ] Añadir tipo con botones rápidos → se guarda
- [ ] `/resumen` → muestra citas + hábitos del día

### 🟡 Bloque 7 — Docker (si tienes Docker instalado)
- [ ] `make docker-build` → construye sin errores
- [ ] `make docker-up` → api + bot arrancan
- [ ] `make docker-logs` → se ven logs de ambos
- [ ] Bot funciona igual que en local
- [ ] `make docker-down` + `make docker-up` → datos persisten (SQLite no se borra)
- [ ] `make docker-db` → abre consola SQLite

---

## 🐛 Si algo falla — cómo documentarlo

```bash
# Crea el diario del día y anota los bugs
# Formato: docs/diarios/YYYY-MM-DD.md

# Ejemplo de entrada de bug:
## 🐛 Bugs encontrados
- [ ] BUG: al pulsar ◀️ en /citas del primer día disponible → mensaje de error
      Archivo: src/bot/handlers/citas.py  Línea aprox: cb_citas_nav
      Reproducción: /citas → ◀️ ◀️ ◀️ hasta fecha muy antigua
```

---

## 🔜 Una vez el checklist esté limpio — F9.8 Multi-usuario

Esto es lo que implica F9.8 para no olvidar nada:

### Cambios en SQLite (`src/db/models.py`)
```python
# Añadir en Appointment y Habit:
user_id = Column(String, nullable=False, index=True)
```

### Cambios en la API (`src/api/routers/*.py`)
```python
# Todos los endpoints filtran por user_id:
GET /appointments/{date}?user_id=123
# O mejor: header X-User-Id: 123
```

### Cambios en el bot (`src/bot/api_client.py`)
```python
# ThdoraApiClient pasa user_id en cada llamada:
# update.effective_user.id  → Telegram siempre lo tiene
```

### Migración de datos existentes
```python
# Script de migración para datos ya en la DB:
# ALTER TABLE appointments ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default'
```

> ⚠️ **No empezar F9.8 hasta que el checklist de prueba en vivo esté 100% limpio.**

---

## 🗺️ Roadmap resumido a partir de aquí

```
AHORA       Prueba en vivo — checklist arriba
F9.8        Multi-usuario (user_id en todo)
F10         Módulo Tracking personal (sueño, estado, sustancias)
F11         Notificaciones proactivas (APScheduler)
F12         IA conversacional (Groq/OpenAI/Whisper)
F13         Gamificación RPG (XP, niveles, rachas)
F14         Telegram Mini App
F15         PWA
F16         React Native
```

---

_Última actualización: 12 abril 2026 — 21:22 CEST_
