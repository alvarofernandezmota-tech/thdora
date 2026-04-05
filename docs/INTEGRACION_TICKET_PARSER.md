# 🧾 Integración Ticket Parser — THDORA

> Cómo integrar el parser de tickets de `image-calculator` en el bot de Telegram.

---

## ¿Qué hace este módulo?

Recibe el texto crudo del OCR de una imagen de ticket/factura y devuelve una lista limpia de conceptos y precios:

```python
texto_ocr = """
MERCADONA S.A.
Leche entera 1L       1,25
Pan molde grande      0,89
Yogur natural x4      1,58
Bolsa reutilizable    0,10
TOTAL                 3,82
IVA 10%               0,35
"""

resultado = await parsear_ticket(texto_ocr)
# [{"concepto": "Leche entera 1L", "precio": 1.25},
#  {"concepto": "Pan molde grande", "precio": 0.89},
#  {"concepto": "Yogur natural x4", "precio": 1.58},
#  {"concepto": "Bolsa reutilizable", "precio": 0.10}]
```

---

## Cómo funciona internamente

```
texto OCR
    ↓
Groq (llama3-8b-8192)
    Prompt: "Extrae concepto y precio de cada línea.
             Ignora TOTAL, IVA, nombre tienda, dirección.
             Devuelve JSON array: [{concepto, precio}]"
    ↓
JSON validado
    ↓
list[dict]  [{"concepto": str, "precio": float}]
```

**Fallback heurístico** (si Groq no disponible):
- Busca líneas con patrón `[texto]  [número decimal]`
- Ignora líneas que contienen palabras clave de la plantilla activa
- Normaliza `1,25` → `1.25`

---

## Archivo a copiar

Cuando `image-calculator` v1.0 esté listo:

```bash
# Copiar desde image-calculator
cp ../image-calculator/nucleo/parser.py src/ai/ticket_parser.py
```

No requiere cambios — la interfaz pública es idéntica.

---

## Handler bot (a implementar en F12)

```python
# src/bot/handlers/tickets.py  (futuro)

from src.ai.ticket_parser import parsear_ticket
from nucleo.lector import LectorImagen  # OCR

async def handle_foto_ticket(update, context):
    # 1. Descargar imagen
    foto = await update.message.photo[-1].get_file()
    path = f"/tmp/{foto.file_id}.jpg"
    await foto.download_to_drive(path)

    # 2. OCR
    lector = LectorImagen(path)
    texto = lector.extraer_texto_completo()  # método a añadir en v1.0

    # 3. Parser IA
    items = await parsear_ticket(texto)

    # 4. Mostrar tabla al usuario con botones inline
    mensaje = "\n".join([
        f"• {item['concepto']}: {item['precio']:.2f}€"
        for item in items
    ])
    total = sum(i['precio'] for i in items)
    await update.message.reply_text(
        f"{mensaje}\n\n💰 Total: {total:.2f}€",
        reply_markup=teclado_confirmar_ticket(items)
    )
```

---

## Variables de entorno necesarias

Ya están configuradas en THDORA — no hay que añadir nada nuevo:

```env
GROQ_API_KEY=tu_key_aqui   # ya existe en .env
GROQ_MODEL=llama3-8b-8192  # ya existe en .env
```

---

## Dependencias nuevas

Solo si `parser.py` usa `httpx` directamente (probable):

```bash
# ya está en requirements.txt de THDORA
httpx>=0.27
```

No se necesita ninguna dependencia nueva.
