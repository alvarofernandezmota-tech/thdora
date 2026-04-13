# 🔌 THDORA — Referencia completa de la API REST

> Todos los endpoints, parámetros, respuestas y comportamientos especiales.
>
> **Navegación:** [README](../README.md) · [ARCHITECTURE](ARCHITECTURE.md) · [FLUJOS_DETALLADOS](FLUJOS_DETALLADOS.md)

---

## Base URL

```
Local:   http://localhost:8000
Docker:  http://api:8000  (desde el contenedor bot)
```

## Autenticación

Ninguna en v1. Preparado para `X-User-Id` header en F11 Multi-usuario.

---

## Health

### `GET /`
- **Respuesta:** `200 OK` `{"status": "ok"}`
- **Usado por:** el bot al arrancar para verificar que la API está lista

---

## Citas — `/appointments`

### `POST /appointments/{date}`
Crea una nueva cita.

```json
// Request body
{
  "time":  "10:30",         // HH:MM — obligatorio
  "name":  "Médico",        // obligatorio
  "type":  "medica",        // medica|personal|trabajo|otra
  "notes": "Dr. García"     // opcional, puede ser ""
}

// Response 201
{
  "id":    1,
  "date":  "2026-04-13",
  "time":  "10:30",
  "name":  "Médico",
  "type":  "medica",
  "notes": "Dr. García",
  "index": 0               // posición ordinal en el día (0, 1, 2…)
}
```

> ⚠️ **`index`** es la posición de la cita en la lista del día, no un ID global.
> Se recalcula al crear/borrar citas. Usar siempre el `index` devuelto por `GET`.

### `GET /appointments/{date}`
Devuelve todas las citas de un día, ordenadas por hora.

```json
// Response 200
[
  {"id": 1, "date": "2026-04-13", "time": "09:00", "name": "Gimnasio", "type": "personal", "notes": "", "index": 0},
  {"id": 2, "date": "2026-04-13", "time": "10:30", "name": "Médico",   "type": "medica",   "notes": "Dr. García", "index": 1}
]
// Si no hay citas: [] con 200 OK
```

### `PUT /appointments/{date}/{index}`
Edita una cita existente. Solo se actualizan los campos enviados.

```json
// Request body (todos opcionales)
{
  "time":  "11:00",
  "name":  "Médico (cambiado)",
  "type":  "medica",
  "notes": "Consulta urgente"
}
// Response 200: cita actualizada completa
// Response 404: cita no encontrada
```

### `DELETE /appointments/{date}/{index}`
Borra una cita. Los índices del resto se recalculan.

```
// Response 204: borrado OK
// Response 404: no encontrada
```

### `GET /appointments/week/{date}`
Devuelve las citas de la semana (lunes–domingo) que contiene `date`.

```json
// Response 200
{
  "2026-04-13": [...],
  "2026-04-14": [...],
  ...
}
```

### `GET /appointments/range/{from_date}/{to_date}`
Citas en un rango de fechas (inclusive ambos extremos).

### `GET /appointments/upcoming/{date}`
Citas desde `date` en adelante, ordenadas por fecha y hora.

### `GET /appointments/{date}/conflict/{time}`
Comprueba si ya hay una cita a esa hora exacta.

```
// Response 200: {cita existente}  → hay conflicto
// Response 404: no hay conflicto
```

> Usado internamente por el bot en el paso `NUEVA_CONFLICT` del flujo `/nueva`.

---

## Hábitos — `/habits`

### `POST /habits/{date}` ← ⚠️ UPSERT
Crea o actualiza un hábito. Si ya existe ese nombre en esa fecha, **lo sobreescribe**.

```json
// Request body
{
  "habit": "Agua",
  "value": "2L"
}
// Response 201: {"id": 1, "date": "2026-04-13", "habit": "Agua", "value": "2L"}
```

> ⚠️ El bot gestiona la lógica de conflicto (`HABITO_CONFLICT`) **antes** de llamar a este endpoint.
> La API siempre sobreescribe sin preguntar.

### `GET /habits/{date}`
Devuelve todos los hábitos del día.

```json
// Response 200 (API)
[
  {"id": 1, "date": "2026-04-13", "habit": "Agua",     "value": "2L"},
  {"id": 2, "date": "2026-04-13", "habit": "Ejercicio", "value": "45min"}
]

// ⚠️ El ThdoraApiClient transforma esto a:
{"Agua": "2L", "Ejercicio": "45min"}
// El bot siempre trabaja con el dict, nunca con la lista raw.
```

### `PUT /habits/{date}/{habit}`
Actualiza el valor de un hábito existente.

```json
// Request: {"value": "2.5L"}
// Response 200: hábito actualizado
// Response 404: no encontrado
```

### `DELETE /habits/{date}/{habit}`
```
// Response 204: borrado
// Response 404: no encontrado
```

### `GET /habits/week/{date}`
Hábitos de la semana que contiene `date`.

### `GET /habits/range/{from_date}/{to_date}`
Hábitos en un rango de fechas.

### `GET /habits/stats/{habit}?days=30`
Historial de un hábito de los últimos N días.

```json
// Response 200
[
  {"date": "2026-04-13", "value": "2L"},
  {"date": "2026-04-12", "value": "1.5L"},
  ...
]
```

---

## HabitConfig — `/habit-config`

### `POST /habit-config/` ← UPSERT por nombre

```json
// Request
{
  "name":       "Sueño",
  "habit_type": "time",       // numeric|time|boolean|text
  "unit":       "h",          // opcional
  "min_val":    0,             // opcional — no validado todavía en API
  "max_val":    24,            // opcional — no validado todavía en API
  "quick_vals": ["6h","7h","8h","9h"],  // opcional
  "xp_rule":    "gte:7"        // opcional — para F15 Gamificación
}
// Response 201: config guardada
```

### `GET /habit-config/{name}`
```
// Response 200: {config}
// Response 404: no existe config para ese hábito
```

### `GET /habit-config/`
Lista todas las configs de hábitos.

### `DELETE /habit-config/{name}`
```
// Response 204: borrado
// Response 404: no encontrado
```

---

## Resumen — `/summary`

### `GET /summary/{date}`

```json
// Response 200
{
  "date":         "2026-04-13",
  "appointments": [...],
  "habits":       {...}
}
```

### `GET /summary/week/{date}`
Resumen de la semana: citas + hábitos por día.

---

## Códigos de error

| Código | Significado |
|--------|-------------|
| `400` | Datos inválidos (body mal formado, formato de fecha incorrecto) |
| `404` | Recurso no encontrado |
| `409` | Conflicto (futuro — no usado en v1) |
| `422` | Validación Pydantic fallida |
| `500` | Error interno de la API |

## Comportamiento del cliente ante errores

```python
# ThdoraApiClient lanza ApiError en cualquier 4xx o 5xx
# El bot captura ApiError y muestra mensaje amigable al usuario
# Nunca crashea el bot por un error de la API

try:
    result = await api.get_appointments(date)
except ApiError as e:
    await msg.reply_text("⚠️ Error al conectar con la API.")
    # e.status_code contiene el código HTTP si hace falta diferenciar
```

---

_Última actualización: 13 abril 2026 — 21:20 CEST_
