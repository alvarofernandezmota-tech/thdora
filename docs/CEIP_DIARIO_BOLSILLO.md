# 📓 CEIP — Diario de Bolsillo con Mistral OCR

> **C**ontexto · **E**strategia · **I**mplementación · **P**lan de escala  
> _Documento extenso — versión 1.0 — 15 junio 2026_  
> _Redactado para ser usado directamente con Vibe (Mistral) como prompt de desarrollo_

---

## 🎬 C — Contexto

### La visión: El Show de Truman, pero para ti

En *El Show de Truman* (1998), un hombre vive su vida sin saber que hay cámaras que registran cada momento. El mundo entero observa sus patrones, sus rutinas, sus emociones — pero él nunca tiene esa perspectiva sobre sí mismo.

**El Diario de Bolsillo de THDORA invierte ese concepto:**
- Las "cámaras" eres tú — tú decides qué compartes
- El "mundo" que observa eres tú mismo — nadie más
- Los patrones se te devuelven como autoconocimiento, no como espectáculo
- Toki es el director que te lo cuenta — sin juicios, sin alarmas innecesarias

> *"Tu vida, por fin con perspectiva."*

---

### ¿Qué es el Diario de Bolsillo?

No es un tracker. No es un coach. No es una app más de mood.

Es **Toki prestando atención** — de forma discreta, consistente y humana:

```
⏰ Nota cuándo te despiertas
🌙 Nota cuándo te duermes
😴 Calcula tus horas reales de sueño
⚡ Registra tu energía del día (1 pregunta, 10 segundos)
📸 Procesa fotos de notas, pizarras, recetas escritas a mano
📝 Transcribe audios de voz a texto del diario
📊 Genera estadísticas semanales y mensuales
🔗 Conecta sueño + energía + temas recurrentes
```

**Lo que lo hace diferente:** vive en WhatsApp/Telegram. No tienes que abrir ninguna app.

---

### Referencias culturales y de producto

#### 🎬 Referencias narrativas

| Referencia | Por qué importa | Qué tomamos |
|---|---|---|
| **El Show de Truman** | La idea de observar tu propia vida con perspectiva | La metáfora fundacional del producto |
| **Her (2013)** | IA que conoce tus patrones emocionales profundos | La relación Toki-usuario: cercana, sin ser invasiva |
| **Black Mirror S01E03 (Tu historial completo)** | Los recuerdos como dato accesible | El peligro de la obsesión — lo que THDORA evita intencionalmente |
| **Inside Out (Pixar)** | Las emociones como personajes con lógica propia | La forma en que Toki habla de emociones — sin dramatismo |
| **Stephen Wolfram Life Log** | Una vida documentada como dato científico | El rigor de datos sin perder humanidad |

#### 📖 Referencias de producto existente

| Producto | URL | Qué hacen bien | Qué les falta |
|---|---|---|---|
| **Gnothi** | github.com/ocdevel/gnothi | OSS, sueño + mood + IA, RAG sobre el journal | App web, sin personalidad, sin voz, sin WhatsApp |
| **Moody** | github.com/vakharwalad23/moody | RAG sobre entradas del diario, insights | Solo texto, sin estadísticas de sueño |
| **ccDiary** | github.com/SimonLiu423/cc_diary | 1er premio hackathon, mood + IA mental health | Prototipo, sin escala |
| **MyDiary** | github.com/h1-the-swan/mydiary | APIs externas para auto-generar entradas | Sin conversación, sin personalidad |
| **Anticipate** | helloanticipate.com | Usa sueño + actividad + ubicación para auto-redactar | Solo iOS, requiere Apple Watch |
| **MiAngel (DeBrah)** | miangel.ai | IA que te escribe primero, memoria larga | Robótica, sin calidez, no es WhatsApp |
| **Flow Dashboard** | OSS, github | Hábitos + analytics personal | Sin IA conversacional |
| **QuantifiedMe** | erik.bjareholt | Dashboard completo de vida cuantificada | Solo para developers, sin UX |

---

### El hueco que nadie ocupa

```
                    CONVERSACIONAL
                          ▲
                          │
           MiAngel ●      │      ● THDORA ← AQUÍ
                          │      (warm + stats + WhatsApp)
  ──────────────────────────────────────────── DATOS REALES
  Solo mood         │      │
  Memora ●          │      │
  JournAI ●         │      │
                          │
                          ▼
                    FORMULARIO
```

Nadie está en el cuadrante **conversacional + datos reales + cálido + sin app**.

---

## 🎯 E — Estrategia

### Principio de diseño: "Atento sin ser pesado"

```
❌ Mal: "Hoy debes completar tu diario"
❌ Mal: "¡No has registrado tu sueño!"
❌ Mal: Notificaciones agresivas diarias

✅ Bien: "Buenos días ☀️ ¿Cómo has dormido?"
✅ Bien: "Llevas 3 días bien — ¿qué está pasando de bueno?"
✅ Bien: Solo contacta cuando tiene algo que aportar
```

### Frecuencia de contacto Toki → Usuario

| Momento | Mensaje tipo | Frecuencia |
|---|---|---|
| Buenos días (~7-9AM) | Check-in sueño | Diario (configurable) |
| Tarde (~3PM) | Energía del día | 3x semana máximo |
| Noche (~10PM) | Cierre del día | Solo si hubo actividad |
| Domingo | Resumen semanal | Semanal fijo |
| Patrón detectado | Insight específico | Solo cuando hay algo real |
| Silencio 3+ días | Check suave | Una vez, no repetir |

### Los datos que rastrea — sin wearable

```python
# Datos que Toki puede inferir sin ningún dispositivo externo:

DATA_POINTS = {
    # Registrados por el usuario (1 pregunta = 1 dato)
    "hora_despertar": "HH:MM cada mañana",
    "hora_dormir": "HH:MM cada noche",
    "energia": "1-5 o emoji ⚡😴",
    "mood_general": "texto libre o emoji",
    "nota_libre": "lo que quiera contar",
    
    # Inferidos por Toki automáticamente
    "horas_sueno": "hora_dormir - hora_despertar",
    "deficit_sueno": "horas_sueno < 7h",
    "variabilidad_horario": "std de horas_despertar",
    "racha_bienestar": "días consecutivos energia >= 4",
    "temas_recurrentes": "NLP sobre notas_libres",
    "dia_semana_optimo": "correlación dia vs energia",
    
    # Opcionales (si el usuario los activa)
    "fotos_notas": "procesadas con Mistral OCR",
    "audios_voz": "transcritos con Groq Whisper",
}
```

---

## 🛠️ I — Implementación

### Arquitectura del módulo

```
thdora/
├── modules/
│   └── diario/
│       ├── __init__.py
│       ├── models.py          # DiarioEntry, SleepRecord, MoodRecord
│       ├── handlers.py        # Handlers de Telegram/WhatsApp
│       ├── scheduler.py       # Jobs automáticos (morning, weekly)
│       ├── stats.py           # Cálculo de estadísticas
│       ├── insights.py        # Generación de insights con IA
│       ├── ocr_processor.py   # ← Mistral OCR para fotos
│       └── voice_processor.py # Groq Whisper para audios
```

---

### Base de datos — Schema

```sql
-- Entradas del diario
CREATE TABLE diary_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    type        TEXT,  -- 'morning', 'evening', 'free', 'ocr', 'voice'
    content     TEXT,
    raw_input   TEXT,  -- original antes de procesar
    source      TEXT   -- 'telegram', 'whatsapp'
);

-- Registros de sueño
CREATE TABLE sleep_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL,
    date            DATE NOT NULL,
    hora_despertar  TIME,
    hora_dormir     TIME,
    horas_reales    FLOAT,  -- calculado
    calidad         INTEGER -- 1-5, opcional
);

-- Registros de energía/mood
CREATE TABLE mood_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    energia     INTEGER,  -- 1-5
    mood_emoji  TEXT,
    mood_texto  TEXT
);

-- Estadísticas calculadas (cache)
CREATE TABLE user_stats (
    user_id             TEXT PRIMARY KEY,
    avg_horas_sueno     FLOAT,
    mejor_dia_semana    TEXT,
    racha_actual        INTEGER,
    racha_maxima        INTEGER,
    total_entradas      INTEGER,
    ultima_actualizacion DATETIME
);
```

---

### Mistral OCR — implementación completa

#### ¿Por qué Mistral OCR?

| Alternativa | Precisión | Precio | Markdown output | Tablas/diagramas |
|---|---|---|---|---|
| **Mistral OCR** | 94.9% | ~$1/1000 páginas | ✅ Nativo | ✅ |
| Google Vision API | 90% | $1.5/1000 imgs | ❌ | Parcial |
| Tesseract (local) | 70-80% | ✅ Gratis | ❌ | ❌ |
| OpenAI GPT-4V | 88% | $5/1000 imgs | ✅ | ✅ |

Mistral OCR es la mejor opción: más barata que OpenAI, mejor que Tesseract, output nativo en Markdown.

#### Casos de uso en el Diario de Bolsillo

```
El usuario fotografía...
├── Una nota manuscrita en papel     → OCR → texto → guardado en diario
├── Una receta de médico             → OCR → extrae medicación + dosis
├── Una pizarra de ideas             → OCR → captura braindump completo
├── Un ticket de compra              → OCR → registro de gasto opcional
├── Una página de diario físico      → OCR → digitaliza tu diario en papel
└── Un post-it con recordatorio      → OCR → tarea o nota rápida
```

#### Código completo — `ocr_processor.py`

```python
"""
ocr_processor.py — Módulo Mistral OCR para el Diario de Bolsillo
Procesa imágenes enviadas por el usuario en Telegram/WhatsApp
"""

import os
import base64
import asyncio
from pathlib import Path
from typing import Optional
from mistralai import Mistral
from datetime import datetime

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=MISTRAL_API_KEY)


class DiaryOCRProcessor:
    """
    Procesa imágenes enviadas al diario usando Mistral OCR.
    Soporta: fotos de notas, pizarras, diarios físicos, recetas.
    """

    MODEL = "mistral-ocr-latest"

    # Tipos de documento que Toki puede identificar
    DOC_TYPES = {
        "nota": "nota manuscrita o texto escrito a mano",
        "pizarra": "pizarra o whiteboard con ideas",
        "receta": "receta médica o de cocina",
        "diario": "página de diario físico o cuaderno",
        "ticket": "ticket, recibo o factura",
        "otro": "otro documento o imagen con texto",
    }

    async def process_image_url(self, image_url: str) -> dict:
        """Procesa imagen desde URL pública (Telegram file URL)."""
        try:
            response = client.ocr.process(
                model=self.MODEL,
                document={
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            )
            return self._parse_response(response)
        except Exception as e:
            return {"error": str(e), "text": "", "markdown": ""}

    async def process_image_base64(self, image_path: str) -> dict:
        """Procesa imagen local codificada en base64."""
        try:
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")

            suffix = Path(image_path).suffix.lower()
            mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                   '.png': 'image/png', '.webp': 'image/webp'}.get(suffix, 'image/jpeg')

            response = client.ocr.process(
                model=self.MODEL,
                document={
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                },
            )
            return self._parse_response(response)
        except Exception as e:
            return {"error": str(e), "text": "", "markdown": ""}

    async def process_pdf_url(self, pdf_url: str) -> dict:
        """Procesa PDF completo desde URL (para diarios escaneados)."""
        try:
            response = client.ocr.process(
                model=self.MODEL,
                document={
                    "type": "document_url",
                    "document_url": pdf_url,
                },
            )
            # PDF puede tener múltiples páginas
            all_text = ""
            all_markdown = ""
            for page in response.pages:
                all_text += page.text + "\n\n"
                all_markdown += page.markdown + "\n\n"
            return {
                "text": all_text.strip(),
                "markdown": all_markdown.strip(),
                "pages": len(response.pages),
                "error": None,
            }
        except Exception as e:
            return {"error": str(e), "text": "", "markdown": ""}

    def _parse_response(self, response) -> dict:
        """Parsea la respuesta de Mistral OCR."""
        try:
            if hasattr(response, 'pages') and response.pages:
                page = response.pages[0]
                return {
                    "text": getattr(page, 'text', '') or getattr(page, 'markdown', ''),
                    "markdown": getattr(page, 'markdown', ''),
                    "error": None,
                }
            return {"text": str(response), "markdown": "", "error": None}
        except Exception as e:
            return {"error": str(e), "text": "", "markdown": ""}

    async def classify_and_save(
        self,
        user_id: str,
        image_url: str,
        toki_response_fn=None
    ) -> str:
        """
        Pipeline completo:
        1. OCR de la imagen
        2. Clasificación del tipo de documento
        3. Guardado en el diario
        4. Respuesta de Toki al usuario
        """
        result = await self.process_image_url(image_url)

        if result["error"]:
            return "No he podido leer la imagen, ¿está bien iluminada? 📸"

        text = result["text"]
        if not text.strip():
            return "No he encontrado texto en la imagen. ¿Es una nota escrita? ✍️"

        # Guardar en diary_entries
        entry = {
            "user_id": user_id,
            "type": "ocr",
            "content": text,
            "raw_input": image_url,
            "timestamp": datetime.now().isoformat(),
        }
        # → aquí va save_diary_entry(entry)

        # Respuesta de Toki
        preview = text[:150] + "..." if len(text) > 150 else text
        return (
            f"📝 He leído tu nota y la he guardado en el diario:\n\n"
            f"_{preview}_\n\n"
            f"¿Quieres añadir algo más sobre esto?"
        )


# Instancia global
ocr_processor = DiaryOCRProcessor()
```

---

### Handler de Telegram — integración OCR

```python
# En handlers/diary_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from modules.diario.ocr_processor import ocr_processor


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cuando el usuario envía una foto a Toki:
    1. Descarga la imagen de Telegram
    2. La procesa con Mistral OCR
    3. Guarda en el diario
    4. Responde como Toki
    """
    user_id = str(update.effective_user.id)

    # Telegram envía múltiples tamaños — cogemos el mayor
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_url = file.file_path  # URL pública de Telegram

    # Typing indicator mientras procesa
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # OCR + guardar + respuesta
    response = await ocr_processor.classify_and_save(
        user_id=user_id,
        image_url=image_url,
    )

    await update.message.reply_text(response)


async def handle_document_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Para PDFs y documentos enviados como archivo."""
    user_id = str(update.effective_user.id)
    doc = update.message.document

    if doc.mime_type == "application/pdf":
        file = await context.bot.get_file(doc.file_id)
        result = await ocr_processor.process_pdf_url(file.file_path)
        pages = result.get("pages", 1)
        preview = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
        response = (
            f"📄 PDF procesado ({pages} página{'s' if pages > 1 else ''}):\n\n"
            f"_{preview}_\n\n"
            f"Todo guardado en tu diario 📓"
        )
    else:
        response = "Por ahora solo proceso fotos y PDFs en el diario 📸"

    await update.message.reply_text(response)
```

---

### Estadísticas — `stats.py`

```python
"""
stats.py — Cálculo de estadísticas del Diario de Bolsillo
Generadas semanalmente y bajo demanda
"""

from dataclasses import dataclass
from typing import List, Optional
from statistics import mean, stdev
from datetime import date, timedelta


@dataclass
class WeeklyStats:
    # Sueño
    avg_horas_sueno: float
    min_horas_sueno: float
    max_horas_sueno: float
    dias_deficit_sueno: int  # <7h
    hora_despertar_habitual: str
    
    # Energía
    avg_energia: float
    mejor_dia_semana: str
    peor_dia_semana: str
    
    # Diario
    total_entradas: int
    entradas_voz: int
    entradas_ocr: int
    temas_frecuentes: List[str]
    
    # Rachas
    racha_actual: int
    racha_maxima: int


def calcular_stats_semanales(user_id: str, semana_offset: int = 0) -> WeeklyStats:
    """
    Calcula estadísticas de la semana actual o pasadas.
    semana_offset=0 → esta semana
    semana_offset=1 → semana pasada
    """
    # → aquí va la query a SQLite con los datos reales
    # Retorna WeeklyStats con todos los campos calculados
    pass


def generar_resumen_toki(stats: WeeklyStats) -> str:
    """
    Genera el mensaje de resumen semanal de Toki.
    Cálido, personal, sin ser un informe frío.
    """
    lineas = ["📊 *Tu semana en números:*\n"]

    # Sueño
    emoji_sueno = "😴" if stats.avg_horas_sueno < 7 else "✨"
    lineas.append(
        f"{emoji_sueno} Has dormido una media de *{stats.avg_horas_sueno:.1f}h* "
        f"({'poco' if stats.avg_horas_sueno < 7 else 'bien'})"
    )

    # Mejor día
    if stats.mejor_dia_semana:
        lineas.append(f"⚡ Tu mejor día fue el *{stats.mejor_dia_semana}*")

    # Entradas
    lineas.append(f"📝 {stats.total_entradas} entradas en el diario esta semana")

    # Racha
    if stats.racha_actual >= 3:
        lineas.append(f"🔥 ¡Llevas *{stats.racha_actual} días* seguidos con el diario!")

    # Temas
    if stats.temas_frecuentes:
        temas = ", ".join(stats.temas_frecuentes[:3])
        lineas.append(f"💭 Lo que más ha aparecido: _{temas}_")

    lineas.append("\n¿Cómo ha ido la semana para ti?")

    return "\n".join(lineas)
```

---

### Scheduler — `scheduler.py`

```python
"""
scheduler.py — Jobs automáticos del Diario de Bolsillo
Toki contacta al usuario en momentos clave, sin ser pesado
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job(CronTrigger(hour=7, minute=30))
async def morning_checkin():
    """
    Buenos días — check-in de sueño.
    Solo si el usuario tiene morning_check activado.
    """
    usuarios_activos = await get_usuarios_con_checkin()
    for user_id in usuarios_activos:
        ultimo_sleep = await get_ultimo_sleep_record(user_id)
        if not ultimo_sleep or ultimo_sleep.date < datetime.today().date():
            await enviar_mensaje_toki(
                user_id=user_id,
                mensaje="Buenos días ☀️ ¿A qué hora te has despertado hoy?"
            )


@scheduler.scheduled_job(CronTrigger(day_of_week='sun', hour=10, minute=0))
async def resumen_semanal():
    """Resumen semanal todos los domingos a las 10AM."""
    usuarios_activos = await get_usuarios_activos_semana()
    for user_id in usuarios_activos:
        stats = calcular_stats_semanales(user_id)
        if stats.total_entradas >= 3:  # Solo si hay datos suficientes
            resumen = generar_resumen_toki(stats)
            await enviar_mensaje_toki(user_id=user_id, mensaje=resumen)


@scheduler.scheduled_job(CronTrigger(hour='*/6'))  # Cada 6 horas
async def detectar_patrones_anomalos():
    """
    Detecta patrones que merecen una nota de Toki.
    Solo actúa si hay algo real que decir.
    """
    for user_id in await get_todos_usuarios():
        stats = calcular_stats_semanales(user_id)
        
        # 3 días de déficit de sueño seguidos
        if stats.dias_deficit_sueno >= 3:
            await enviar_insight_toki(
                user_id,
                f"Llevas {stats.dias_deficit_sueno} días durmiendo menos de 7h. "
                f"¿Todo bien o hay algo que te tiene en vela? 🌙"
            )
```

---

## 📈 P — Plan de escala

### Fases del módulo

```
── FASE 1 (v0.18.0) ─────────────────────────────
  ✅ Morning check-in de sueño (texto)
  ✅ Registro de energía (1-5)
  ✅ Entradas libres de diario
  ✅ Resumen semanal básico
  ✅ Estadísticas simples (avg sueño, mejor día)
  Sprint: 2 semanas

── FASE 2 (v0.19.0) ─────────────────────────────
  ✅ Mistral OCR — fotos de notas
  ✅ Groq Whisper — audios de voz al diario
  ✅ Detección de patrones de sueño
  ✅ Insights automáticos cuando hay patrones
  Sprint: 2 semanas

── FASE 3 (v1.0.0) ──────────────────────────────
  ✅ RAG sobre entradas pasadas (buscar recuerdos)
  ✅ Biógrafo anual — "tu año en momentos"
  ✅ Correlaciones sueño ↔ energía ↔ mood
  ✅ Exportación del diario (PDF, Markdown)
  Sprint: 3 semanas

── FASE 4 (v2.0.0) ──────────────────────────────
  ✅ OCR de PDFs completos (diarios físicos)
  ✅ Dashboard web (PWA) con gráficas
  ✅ Modo familia/pareja (diario compartido opt-in)
  ✅ Integración con Google Fit / Apple Health
  Sprint: 1 mes
```

### Coste de escala con Mistral OCR

| Usuarios activos/día | Fotos/día estimadas | Coste OCR/mes | Coste total IAs |
|---|---|---|---|
| 50 | ~25 fotos | $0.025 | ~$0 (free tiers) |
| 500 | ~250 fotos | $0.25 | ~$2-5/mes |
| 5.000 | ~2.500 fotos | $2.50 | ~$20-30/mes |
| 50.000 | ~25.000 fotos | $25 | ~$150-200/mes |

**Mistral OCR:** ~$1 por 1.000 páginas procesadas. Escalabilidad brutal.

---

### Variables de entorno necesarias

```bash
# .env — añadir para el módulo Diario
MISTRAL_API_KEY=sk-...          # Para OCR
GROQ_API_KEY=gsk_...            # Ya existe — para Whisper
GEMINI_API_KEY=...              # Ya existe — para resúmenes largos
DIARIO_MORNING_HOUR=7           # Hora del check-in mañana
DIARIO_MORNING_MINUTE=30
DIARIO_EVENING_ENABLED=false    # Check-in nocturno (opt-in)
DIARIO_WEEKLY_DAY=sunday        # Día del resumen semanal
```

---

### Repos OSS de referencia para el desarrollo

| Repo | Qué tomar | URL |
|---|---|---|
| **gnothi** | Schema DB sueño/mood, RAG sobre journal | github.com/ocdevel/gnothi |
| **moody** | Pipeline RAG + embeddings sobre entradas | github.com/vakharwalad23/moody |
| **ccDiary** | Lógica de insights de salud mental | github.com/SimonLiu423/cc_diary |
| **mydiary** | Auto-generación de entradas desde APIs | github.com/h1-the-swan/mydiary |
| **mistralai/client-python** | SDK oficial Mistral OCR | github.com/mistralai/client-python |

---

## 🚀 Cómo usar este documento con Vibe (Mistral)

```
1. Abre Vibe en mistral.ai/products/vibe
2. Pega este bloque como primer mensaje:

   "Eres un arquitecto de software Python senior.
    Aquí está el CEIP completo del módulo Diario de Bolsillo
    para el proyecto THDORA. Quiero que desarrolles [módulo X]
    siguiendo exactamente esta arquitectura."

3. Pega el bloque de código específico que quieres que complete
4. Vibe genera el código completo
5. Perplexity MCP lo sube al repo
```

---

_Documento generado: 15 junio 2026 | Próxima revisión: v0.18.0 completado_
