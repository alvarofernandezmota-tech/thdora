# 🌐 Ecosistema THEA IA — Relación entre repos

> Este documento describe cómo `thdora` e `image-calculator` trabajan de forma independiente pero están diseñados para integrarse dentro del ecosistema THEA IA.

---

## Los dos repos

| Repo | Qué es | Estado |
|------|--------|--------|
| [`thdora`](https://github.com/alvarofernandezmota-tech/thdora) | Asistente personal IA — Bot Telegram + FastAPI + SQLite | v0.8.1 ✅ |
| [`image-calculator`](https://github.com/alvarofernandezmota-tech/image-calculator) | OCR + Parser IA de documentos (tickets, facturas) | v0.5 ✅, v1.0 🔶 |

Cada repo funciona de forma **completamente independiente**. No hay dependencias cruzadas en el código — la integración es por copia de módulo cuando esté listo.

---

## Arquitectura del ecosistema

```
┌─────────────────────────────────────────────────────────────┐
│                     THEA IA (ecosistema)                    │
│                                                             │
│  ┌─────────────────────┐     ┌─────────────────────────┐   │
│  │      THDORA         │     │    IMAGE-CALCULATOR      │   │
│  │                     │     │                          │   │
│  │  Bot Telegram       │     │  OCR (Tesseract)         │   │
│  │  FastAPI REST       │◄────│  Parser IA (Groq)        │   │
│  │  SQLite             │     │  Tabla editable (GUI)    │   │
│  │  Citas / Hábitos    │     │  App desktop standalone  │   │
│  │  Tracking gastos    │     │                          │   │
│  └─────────────────────┘     └─────────────────────────┘   │
│                                                             │
│  Groq API (gratuita) ←──── usada por ambos repos            │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de integración — Ticket parser en el bot

Cuando `image-calculator` v1.0 esté listo, el flujo dentro de THDORA será:

```
[usuario]  manda foto de ticket por Telegram
       ↓
[bot]      recibe la imagen (FileHandler)
       ↓
[nucleo/lector.py]      OCR → texto crudo       ← de image-calculator
       ↓
[src/ai/ticket_parser.py]   Groq → JSON limpio  ← de image-calculator
       [{"concepto": "Leche entera", "precio": 1.25}, …]
       ↓
[bot]      muestra tabla editable con botones inline
       ↓
[usuario]  confirma o edita los datos
       ↓
[src/db]   guarda los gastos en SQLite
```

---

## Módulo que viaja entre repos

El módulo `nucleo/parser.py` de `image-calculator` se copia como `src/ai/ticket_parser.py` en `thdora` cuando esté listo y testeado.

**No es una dependencia de paquete** — es una copia directa. Esto mantiene cada repo completamente autónomo.

```python
# En image-calculator (desarrollo y pruebas)
from nucleo.parser import parsear_ticket

# En thdora (producción, misma lógica)
from src.ai.ticket_parser import parsear_ticket

# Misma función, mismo contrato:
# entrada: str (texto OCR crudo)
# salida:  list[dict]  [{"concepto": str, "precio": float}]
```

---

## Groq: patrón compartido

Ambos repos usan Groq con el mismo patrón:

```python
# thdora: src/ai/groq_client.py  (YA EXISTE)
# image-calculator: nucleo/parser.py  (A IMPLEMENTAR, mismo patrón)

# .env en cada repo:
GROQ_API_KEY=tu_key_aqui
GROQ_MODEL=llama3-8b-8192   # opcional
```

---

## Dónde encaja en el ROADMAP de THDORA

| Fase THDORA | Relación con image-calculator |
|---|---|
| **F12 — IA conversacional** | El parser de tickets es la primera habilidad visual del bot |
| **F10 — Tracking personal** | Los gastos extraídos del ticket alimentan el tracking diario |
| **F9.8 — Multi-usuario** | Cada usuario tiene su historial de tickets separado |

---

## Desarrollo independiente paso a paso

| Paso | Repo | Tarea |
|------|------|-------|
| 1 | `image-calculator` | Implementar `nucleo/parser.py` con Groq |
| 2 | `image-calculator` | GUI tabla editable + selector de modo |
| 3 | `image-calculator` | Tests del parser + release v1.0 |
| 4 | `thdora` | Copiar como `src/ai/ticket_parser.py` |
| 5 | `thdora` | Handler bot: recibir foto → parsear → tabla inline |
| 6 | `thdora` | Guardar gastos en SQLite (F10 tracking) |
