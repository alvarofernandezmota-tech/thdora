# 🖼️ `src/core/ocr` — Módulo OCR

Extracción de números desde imágenes para el ecosistema THDORA.

## Posición en la arquitectura

```
src/
├── core/
│   ├── ocr/          ← ESTÁS AQUÍ
│   │   ├── reader.py       ← carga + preprocesado + OCR
│   │   └── operations.py   ← operaciones sobre números
│   └── ai/           ← futuro: ImageAgent llama a reader.py
├── api/
│   └── routers/
│       └── ocr.py        ← futuro: POST /ocr/extract
└── bot/
    └── handlers/
        └── ocr.py        ← futuro: handler /imagen
```

## Uso actual (standalone)

```python
from src.core.ocr import ImageReader, ImageOperations

reader = ImageReader()
ops    = ImageOperations()

a = reader.extraer_numero("ticket_a.png")   # 42.0
b = reader.extraer_numero("ticket_b.jpg")   # 18.0

print(ops.aplicar("Suma", a, b))            # "42.0 + 18.0 = 60.0"
print(ops.aplicar("Comparar", a, b))        # "42.0 > 18.0  →  A es mayor"
```

## Dependencias OCR

No se instalan automáticamente (son opcionales hasta que se active el módulo):

```bash
pip install pillow opencv-python pytesseract
```

Además necesitas **Tesseract** en el sistema:

```bash
# macOS
brew install tesseract

# Linux
sudo apt install tesseract-ocr

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki
```

## Hoja de ruta de integración

| Fase | Qué | Dónde |
|------|-----|-------|
| **Ahora** | Módulo standalone | `src/core/ocr/` |
| **F12** | `ImageAgent` llama a `ImageReader` | `src/core/ai/image_agent.py` |
| **F12+** | Endpoint REST `POST /ocr/extract` | `src/api/routers/ocr.py` |
| **F12+** | Handler bot `/imagen` | `src/bot/handlers/ocr.py` |
| **CEO OS** | Agente procesa tickets, facturas, datos en foto | `src/core/ai/agents/image_agent.py` |
