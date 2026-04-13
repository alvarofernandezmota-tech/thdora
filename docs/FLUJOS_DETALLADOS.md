# 🔄 THDORA — Flujos detallados

> Documentación técnica de todos los flujos del bot: estados, transiciones, casos borde y comportamientos no obvios.
>
> **Navegación:** [README](../README.md) · [ARCHITECTURE](ARCHITECTURE.md) · [API_REFERENCE](API_REFERENCE.md) · [CONVENCIONES](CONVENCIONES.md)

---

## Flujo `/nueva` — Crear cita

### Estados del ConversationHandler

```
Entry points:
  /nueva (comando)
  quick_nueva_{date} (botón ➕ del menú o vista de citas)

NUEVA_DATE
  └── Texto libre: "hoy", "mañana", "27/03", "lunes"…
      → parse con _parse_date_flex()
      → si inválido: pide de nuevo (no avanza)
      → si válido: → NUEVA_FRANJA

NUEVA_FRANJA
  └── Botones: [🌅 Mañana 6-14] [🌆 Tarde 14-22] [🌙 Noche 22-6] [✏️ Exacta]
      → Mañana/Tarde/Noche: → NUEVA_HORA_PUNTO
      → Exacta: → NUEVA_TIME

NUEVA_HORA_PUNTO
  └── Botones: hora en punto dentro de la franja (ej: 06:00…13:00)
      → Seleccionar hora: → NUEVA_HORA_CUARTO
      → [🕐 Ver cuartos]: → NUEVA_HORA_CUARTO
      → [✏️ Exacta]: → NUEVA_TIME

NUEVA_HORA_CUARTO
  └── Botones: [HH:00] [HH:15] [HH:30] [HH:45] [✏️ Exacta]
      → Seleccionar cuarto: → NUEVA_CONFLICT (comprueba)
      → Exacta: → NUEVA_TIME

NUEVA_TIME
  └── Texto libre: "10:30", "930" (normaliza a HH:MM)
      → HH:MM inválido: pide de nuevo
      → HH:MM válido: → NUEVA_CONFLICT (comprueba)

NUEVA_CONFLICT  ← ⚠️ estado especial
  └── check_appointment_conflict(date, time)
      → Sin conflicto: salta directamente → NUEVA_NOMBRE
      → Con conflicto: muestra aviso ⚠️ + [Cambiar hora] [Continuar]
          → Cambiar hora: → NUEVA_FRANJA  ← ⚠️ vuelve a FRANJA, no a DATE
          → Continuar: → NUEVA_NOMBRE

NUEVA_NOMBRE
  └── Texto libre
      → vacío: pide de nuevo
      → válido: → NUEVA_TYPE

NUEVA_TYPE
  └── Botones: [Médica] [Personal] [Trabajo] [Otra]
      → Seleccionar: → NUEVA_NOTES

NUEVA_NOTES
  └── Texto libre o /skip
      → Guarda cita via POST /appointments/{date}
      → Reprograma jobs del scheduler (cuando F12 esté implementado)
      → END
```

### Casos borde importantes

| Caso | Comportamiento |
|------|----------------|
| Fecha pasada | Se acepta — se puede crear cita en el pasado |
| Conflicto de hora | Aviso ⚠️ pero no bloquea — se puede continuar igualmente |
| Volver de conflicto | Vuelve a `NUEVA_FRANJA`, no a `NUEVA_DATE` — la fecha se mantiene |
| Hora en formato `930` | Se normaliza a `09:30` automáticamente |
| `/cancelar` en cualquier punto | Limpia `user_data` y termina el flujo |
| Entry point desde botón | La fecha se extrae del callback_data `quick_nueva_{date}` |

---

## Flujo `/habito` — Registrar hábito

### Estados del ConversationHandler

```
Entry points:
  /habito (comando)
  quick_habito_{date} (botón ➕ del menú o vista de hábitos)

HABITO_NOMBRE
  └── Texto libre
      → vacío: pide de nuevo
      → válido: consulta HabitConfig de ese nombre
          → Con config: muestra botones rápidos + hint de tipo/unidad → HABITO_VALUE
          → Sin config: pide valor con texto libre → HABITO_VALUE

HABITO_VALUE
  └── Botón rápido (hval_{valor}) o texto libre
      → [✏️ Otro]: pide texto libre
      → valor con "+" (ej: +2L): acumula directamente → END
      → valor sin "+" y hábito ya existe hoy: → HABITO_CONFLICT
      → valor sin "+" y hábito no existe: guarda directamente → END

HABITO_CONFLICT
  └── Botones: [Sobreescribir] [Sumar] [Cancelar]
      → Sobreescribir: PUT /habits/{date}/{habit} con nuevo valor → END
      → Sumar: calcula _accumulate_value(existing, "+"+new) → PUT → END
      → Cancelar: descarta, limpia user_data → END
```

### Flujo editar hábito

```
Entry point: callback ^he_{date}_{habit}

EDIT_HAB_NOMBRE
  └── Texto libre o /skip
      → /skip: mantiene nombre actual
      → texto: nuevo nombre guardado en user_data
      → Consulta HabitConfig del nombre nuevo → EDIT_HAB_VALUE

EDIT_HAB_VALUE
  └── Botón rápido, texto libre o /skip
      → /skip: mantiene valor actual
      → Si nombre cambió: DELETE viejo + POST nuevo  ← ⚠️ internamente
      → Si solo valor: PUT /habits/{date}/{habit}
      → END
```

### Lógica de acumulación — reglas exactas

```python
# Función: _accumulate_value(existing, new_input)

# Caso 1: new_input empieza con "+" → SUMA
_accumulate_value("6h",  "+2h")    → "8h"
_accumulate_value("1.5L", "+0.5L") → "2.0L"
_accumulate_value(None,  "+3")     → "3"        # sin base: usa el incremento
_accumulate_value("5",   "+3")     → "8"

# Caso 2: new_input SIN "+" → SOBREESCRIBE (o pregunta si ya existe)
_accumulate_value("6h",  "8h")     → "8h"       # solo desde flujo de conflicto
_accumulate_value(None,  "8h")     → "8h"        # nuevo hábito, directo

# Extracción de número y unidad:
# "2.5L" → (2.5, "L"),  "30min" → (30, "min"),  "8h" → (8, "h"),  "5" → (5, "")
# Si unidades no coinciden → concatena en lugar de sumar
# Ej: _accumulate_value("8h", "+30min") → "8h30min"  (no convierte)
```

### Formatos de valor por tipo de hábito

| Tipo | Ejemplos válidos | Acumula con `+` | Botones rápidos típicos |
|------|-----------------|-----------------|------------------------|
| `numeric` | `8`, `7.5`, `10`, `0` | ✅ suma numérica | `1,2,3,4,5` |
| `time` | `8h`, `90min`, `1.5h` | ✅ suma numérica + unidad | `6h,7h,8h,9h` |
| `boolean` | `sí`, `no`, `1`, `0` | ❌ no acumula | `sí,no` |
| `text` | cualquier texto | ❌ no acumula | sin botones |
| sin config | cualquier texto | ✅ si empieza con `+` | sin botones |

> ⚠️ El tipo `boolean` no bloquea acumulación a nivel de código — es responsabilidad del usuario no intentarlo.
> La validación de rango (`min_val`, `max_val`) está modelada en la DB pero **no está implementada en la API todavía**.

---

## Flujo `/config` — Configuración actual

```
Entry point: /config (comando)

CFG_NOMBRE
  └── Muestra configs existentes + pide nombre del hábito a configurar
      → texto libre → CFG_TYPE

CFG_TYPE
  └── Botones: [🔢 Numérico] [⏱️ Tiempo] [✅ Sí/No] [📝 Texto]
      → boolean: guarda directamente → END  (no necesita unidad ni botones)
      → resto: → CFG_UNIT

CFG_UNIT
  └── Texto libre o /skip
      → guarda unidad en user_data → CFG_QUICK

CFG_QUICK
  └── Valores separados por comas (ej: "6h,7h,8h") o /skip
      → POST /habit-config/ (upsert)
      → END
```

> 🔜 En F12 Notificaciones, `/config` tendrá un menú raíz con
> `[💪 Hábitos]` y `[🔔 Notificaciones]` antes de este flujo.
> Ver diseño completo en [F12_NOTIFICACIONES_DESIGN.md](F12_NOTIFICACIONES_DESIGN.md).

---

## Flujo acumulación rápida (fuera de ConversationHandler)

Este flujo ocurre **sin ConversationHandler** — usa `user_data` directamente:

```
Usuario pulsa [➕] en un hábito de la lista
    └── cb_hab_add() — guarda date + habit en user_data
            └── pide texto libre

Usuario escribe texto libre (cualquier mensaje)
    └── _route_free_text() en main.py
            └── si user_data["acum_hab_nombre"] existe → cb_hab_add_value()
                    └── _accumulate_value(existing, input)
                        PUT /habits/{date}/{habit}
                        limpia user_data
```

> ⚠️ Este flujo puede interceptar mensajes inesperados si el usuario
> escribe texto libre después de pulsar ➕ sin completar la acumulación.
> Solución: `/cancelar` siempre limpia `user_data`.

---

_Última actualización: 13 abril 2026 — 21:20 CEST_
