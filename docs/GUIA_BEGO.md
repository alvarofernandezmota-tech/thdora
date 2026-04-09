# 🐍 Guía Begoña — De los ejercicios a un proyecto real

> Después de completar los 6 ejercicios de
> [`ejerciciosbego`](https://github.com/alvarofernandezmota-tech/ejerciciosbego),
> este documento te muestra cómo todo eso vive en **THDORA**:
> un bot de Telegram real escrito en Python.
>
> Cada sección conecta un concepto que ya sabes con el archivo exacto del proyecto donde se usa.

---

## ¿Qué es THDORA?

THDORA es un asistente personal que vive en Telegram.
Desde el móvil puedes:
- Crear y ver citas (`/nueva`, `/citas`)
- Registrar hábitos diarios (`/habito`, `/habitos`)
- Ver el resumen del día (`/resumen`)

Por dentro está hecho con Python, dividido en capas que se hablan entre sí.

---

## 🗺️ El mapa del proyecto

```
thdora/
├── src/
│   ├── bot/                     ← Lo que ves en Telegram
│   │   ├── handlers.py           ← Un comando = una función
│   │   ├── api_client.py         ← Habla con la API
│   │   └── main.py               ← Arranque del bot
│   ├── api/                     ← La "ventanilla" que recibe peticiones
│   │   └── routers/
│   │       ├── appointments.py   ← Rutas de citas
│   │       ├── habits.py         ← Rutas de hábitos
│   │       └── summary.py        ← Ruta de resumen
│   ├── core/                    ← El cerebro — lógica de negocio
│   │   ├── interfaces/
│   │   │   └── abstract_lifemanager.py   ← Clase abstracta (contrato)
│   │   └── impl/
│   │       ├── sqlite_lifemanager.py     ← Implementación real (producción)
│   │       ├── json_lifemanager.py       ← Implementación JSON
│   │       └── memory_lifemanager.py     ← Implementación en memoria (tests)
│   └── db/                      ← Base de datos
│       ├── models.py             ← Tablas como clases Python
│       └── base.py               ← Conexión a SQLite
├── tests/                       ← Pruebas automáticas
│   ├── unit/                    ← Prueba una función sola
│   ├── integration/             ← Prueba varias capas juntas
│   └── e2e/                     ← Prueba el flujo completo
├── docs/                        ← Toda la documentación
├── README.md                    ← Portada del proyecto
├── CHANGELOG.md                 ← Historial de cambios
├── ROADMAP.md                   ← Planes futuros
└── Makefile                     ← Atajos para arrancar todo
```

---

## 📚 Ejercicio 01 → Variables

**Lo que aprendiste:**
```python
nombre = "Begoña"
edad   = 25
es_mayor = True
```

**Dónde vive en THDORA:**

Las variables de configuración del proyecto viven en el archivo `.env`.
No se ponen dentro del código para que sean seguras (el token de Telegram es como una contraseña):

```bash
# .env.example
TELEGRAM_BOT_TOKEN=tu_token_aqui        # str — el token del bot
THDORA_API_URL=http://localhost:8000     # str — dirección de la API
THDORA_DB_URL=sqlite:///data/thdora.db  # str — ruta de la base de datos
```

Y en el código se leen así:
```python
import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ← lee la variable del entorno
```

Mismo concepto — variable con nombre y valor — pero el valor viene de fuera del código.

📂 **Archivos:** [`.env.example`](../.env.example) · [`src/bot/main.py`](../src/bot/main.py)

---

## 📚 Ejercicio 02 → Listas

**Lo que aprendiste:**
```python
frutas = ["manzana", "naranja", "plátano"]
for fruta in frutas:
    print(fruta)
```

**Dónde vive en THDORA:**

Cuando pides `/citas`, la API devuelve una lista de citas. Es exactamente lo mismo,
pero cada elemento de la lista es un diccionario con varios campos:

```python
# Lo que devuelve get_appointments() — sqlite_lifemanager.py
citas = [
    {"id": "abc-123", "time": "10:00", "type": "Médico",  "notes": "llevar analítica"},
    {"id": "def-456", "time": "17:00", "type": "Reunión", "notes": ""}
]

# Y en handlers.py se recorre con un for:
for cita in citas:
    texto += f"🕐 {cita['time']} — {cita['type']}\n"
```

📂 **Archivos:** [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py) · [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 03 → Condiciones

**Lo que aprendiste:**
```python
if temperatura >= 30:
    print("Calor")
elif temperatura >= 20:
    print("Agradable")
else:
    print("Frío")
```

**Dónde vive en THDORA:**

El bot decide qué hacer según el mensaje del usuario.
Cada `ConversationHandler` tiene estados y en cada estado una condición:

```python
# handlers.py (simplificado)
async def recibir_fecha(update, context):
    texto = update.message.text

    if texto == "/cancelar":
        return await cmd_cancelar(update, context)  # centinela
    elif es_fecha_valida(texto):
        context.user_data["fecha"] = texto
        await update.message.reply_text("¿A qué hora?")
        return ESPERANDO_HORA
    else:
        await update.message.reply_text("No entendí la fecha. Prueba con 'hoy' o '27/04'")
        return ESPERANDO_FECHA  # repite el mismo estado
```

📂 **Archivo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 04 → Bucles

**Lo que aprendiste:**
```python
for i in range(5):
    print(i)

for fruta in frutas:
    print(fruta)
```

**Dónde vive en THDORA:**

En el resumen del día, el bot recorre la lista de citas y la lista de hábitos para construir el mensaje:

```python
# handlers.py (simplificado)
async def cmd_resumen(update, context):
    resumen = await api.get_summary(fecha)

    texto = f"📅 Resumen de {fecha}\n\n"

    # Bucle sobre citas
    texto += "🗓 CITAS\n"
    for cita in resumen["appointments"]:
        texto += f"  🕐 {cita['time']} — {cita['type']}\n"

    # Bucle sobre hábitos
    texto += "\n📊 HÁBITOS\n"
    for nombre, valor in resumen["habits"].items():
        texto += f"  • {nombre}: {valor}\n"

    await update.message.reply_text(texto)
```

📂 **Archivo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 05 → Funciones

**Lo que aprendiste:**
```python
def saludar_a(nombre):
    print(f"¡Hola, {nombre}!")

def cuadrado(numero):
    return numero ** 2
```

**Dónde vive en THDORA:**

Cada comando del bot es una función. La diferencia con tus ejercicios es que llevan `async` delante — significa que pueden esperar sin bloquear el bot mientras Telegram responde:

```python
# handlers.py
async def cmd_start(update, context):
    """Responde al /start con el menú de bienvenida."""
    await update.message.reply_text(
        "🧠 Hola, soy THDORA. ¿En qué puedo ayudarte?\n"
        "/nueva — Crear cita\n"
        "/citas — Ver citas de hoy\n"
        "/resumen — Resumen del día"
    )

async def cmd_habito(update, context):
    """Inicia el registro de un hábito."""
    await update.message.reply_text("¿Qué hábito quieres registrar?")
    return ESPERANDO_HABITO
```

Y en `api_client.py`, funciones que hablan con la API — como llamar a un servicio externo:

```python
# api_client.py
async def get_appointments(self, date: str) -> list:
    """Pide las citas de un día a la API y las devuelve como lista."""
    response = await self.session.get(f"{self.base_url}/appointments/{date}")
    return response.json()
```

📂 **Archivos:** [`src/bot/handlers.py`](../src/bot/handlers.py) · [`src/bot/api_client.py`](../src/bot/api_client.py)

---

## 📚 Ejercicio 05b → Menú con centinela

**Lo que aprendiste:**
```python
while True:
    opcion = input("Elige: ")
    if opcion == "0":   # ← centinela
        break
```

**Dónde vive en THDORA:**

El bot de Telegram también tiene su centinela: el comando `/cancelar`.
En vez de `break`, usa `ConversationHandler.END` — que para el flujo de la conversación:

```python
# handlers.py
async def cmd_cancelar(update, context):
    """Cancela cualquier operación en curso. Es el centinela del bot."""
    context.user_data.clear()  # limpia los datos a medias
    await update.message.reply_text("❌ Operación cancelada.")
    return ConversationHandler.END  # ← equivalente al break
```

El `ConversationHandler` es como tu `while True` — el bot está siempre escuchando hasta que el usuario para.

📂 **Archivo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 🆕 Lo nuevo: Clases

Despues de los ejercicios aprendes **clases** — plantillas para crear objetos con sus propios datos y métodos.
En THDORA hay tres niveles de clases.

### Nivel 1 — La clase abstracta (el contrato)

Una clase abstracta define **qué** tiene que poder hacer algo, sin decir **cómo**.
Es como un contrato: "si eres un LifeManager, obligatoriamente tienes que saber hacer esto":

```python
# src/core/interfaces/abstract_lifemanager.py
from abc import ABC, abstractmethod

class AbstractLifeManager(ABC):          # ABC = Abstract Base Class
    """
    Contrato que toda implementación de THDORA debe cumplir.
    Define QUÉ se puede hacer, no CÓMO.
    """

    @abstractmethod
    def create_appointment(self, date, time, type, notes=""):
        """Crea una cita. Todas las implementaciones DEBEN tener esto."""
        pass

    @abstractmethod
    def get_appointments(self, date):
        """Devuelve citas de un día."""
        pass

    @abstractmethod
    def log_habit(self, date, habit, value):
        """Registra un hábito."""
        pass

    @abstractmethod
    def get_habits(self, date):
        """Devuelve hábitos de un día."""
        pass

    @abstractmethod
    def get_day_summary(self, date):
        """Devuelve citas + hábitos del día."""
        pass
```

📂 **Archivo:** [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py)

---

### Nivel 2 — Las clases concretas (cómo se hace de verdad)

THDORA tiene 3 implementaciones — las tres cumplen el contrato, pero guardan los datos de formas distintas:

| Clase | Dónde guarda | Cuándo se usa |
|-------|-------------|---------------|
| `MemoryLifeManager` | En RAM (se pierde al cerrar) | Tests rápidos |
| `JsonLifeManager` | En un archivo `.json` | Versión simple |
| `SqliteLifeManager` | En base de datos SQLite | **Producción** |

Ejemplo de la implementación real:

```python
# src/core/impl/sqlite_lifemanager.py
from src.core.interfaces import AbstractLifeManager

class SqliteLifeManager(AbstractLifeManager):   # ← hereda de la clase madre
    """
    Guarda los datos en SQLite.
    Es la implementación activa en producción.
    """

    def __init__(self, db_url: str):
        """Constructor — crea la conexión a la BD al crear el objeto."""
        self.db_url = db_url
        self.session_factory = crear_sesion(db_url)

    def create_appointment(self, date, time, type, notes=""):
        """Guarda la cita en SQLite y devuelve su UUID."""
        with self.session_factory() as session:
            cita = AppointmentModel(
                date=date, time=time, type=type, notes=notes
            )
            session.add(cita)
            session.commit()
            return cita.id

    def get_appointments(self, date):
        """Lee las citas del día desde SQLite."""
        with self.session_factory() as session:
            return session.query(AppointmentModel).filter_by(date=date).all()
```

**Las partes nuevas que verás:**
- `class Hija(Madre)` → herencia — la hija cumple el contrato de la madre
- `def __init__(self, ...)` → constructor, se ejecuta al crear el objeto
- `self.` → guarda datos dentro del propio objeto
- `with session:` → gestor de contexto (cierra la conexión automáticamente)

📂 **Archivos:** [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py) · [`src/core/impl/memory_lifemanager.py`](../src/core/impl/memory_lifemanager.py)

---

### Nivel 3 — Los modelos de base de datos

En `src/db/models.py` las tablas de la base de datos son clases Python.
Cada atributo de la clase es una columna de la tabla:

```python
# src/db/models.py
from sqlalchemy import Column, String, Date
from src.db.base import Base

class AppointmentModel(Base):
    """Tabla 'appointments' en SQLite."""
    __tablename__ = "appointments"

    id    = Column(String, primary_key=True)  # UUID
    date  = Column(Date,   nullable=False)    # 2026-04-09
    time  = Column(String, nullable=False)    # "10:00"
    type  = Column(String, nullable=False)    # "Médico"
    notes = Column(String, default="")        # "llevar analítica"
```

Cada objeto `AppointmentModel` es una fila de la tabla — exactamente como una cita real.

📂 **Archivo:** [`src/db/models.py`](../src/db/models.py)

---

## 🔗 El flujo completo — de Telegram a SQLite y vuelta

Cuando escribes `/nueva` y creas una cita, esto es lo que pasa por dentro:

```
Tú escribes /nueva en Telegram
    ↓
cmd_nueva()              handlers.py       ← función (Ejercicio 05)
    ↓ pregunta fecha, hora, tipo...
recibir_tipo()           handlers.py       ← condiciones if/elif (Ejercicio 03)
    ↓ llama a la API
create_appointment()     api_client.py     ← función async
    ↓ POST /appointments/{date}
router de FastAPI        appointments.py   ← recibe la petición HTTP
    ↓
create_appointment()     SqliteLifeManager ← método de clase (Clases)
    ↓
AppointmentModel         models.py         ← objeto = fila en la BD
    ↓
SQLite                   thdora.db         ← guardado en disco
    ↓
"✅ Cita guardada"       Telegram          ← respuesta al usuario
```

Cada capa hace una sola cosa. Eso se llama **arquitectura limpia**.

---

## 🧪 Tests — comprobar que todo funciona

La carpeta `tests/` tiene pruebas automáticas organizadas en 3 niveles:

| Carpeta | Qué prueba | Ejemplo |
|---------|-----------|--------|
| `unit/` | Una sola función o clase | ¿Devuelve UUID cuando creo una cita? |
| `integration/` | Varias capas juntas | ¿La API + el LifeManager funcionan juntos? |
| `e2e/` | El flujo completo | ¿Del bot a SQLite y vuelta? |

Con `MemoryLifeManager` los tests van rápido — no necesitan base de datos real:

```python
# tests/unit/test_create_appointment.py (ejemplo)
from src.core.impl import MemoryLifeManager
from datetime import date

def test_crear_cita():
    mgr = MemoryLifeManager()                          # clase en memoria
    cita_id = mgr.create_appointment(
        date(2026, 4, 9), "10:00", "Médico"
    )
    citas = mgr.get_appointments(date(2026, 4, 9))
    assert len(citas) == 1                             # comprueba que hay 1 cita
    assert citas[0]["type"] == "Médico"               # comprueba el tipo
```

📂 **Carpeta:** [`tests/`](../tests/)

---

## 📖 Documentación del proyecto

| Archivo | Qué contiene |
|---------|-------------|
| [README.md](../README.md) | Portada — qué es, cómo instalarlo, comandos disponibles |
| [CHANGELOG.md](../CHANGELOG.md) | Historial de cambios versión a versión |
| [ROADMAP.md](../ROADMAP.md) | Fases del proyecto y estado actual |
| [docs/architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) | Cómo están organizadas las capas |
| [docs/architecture/repo-map.md](architecture/repo-map.md) | Mapa detallado de cada archivo |
| [docs/modules/bot.md](modules/bot.md) | Cómo funciona el módulo bot |
| [docs/modules/api.md](modules/api.md) | Cómo funciona la API |
| [docs/modules/core.md](modules/core.md) | Cómo funciona el core |
| [docs/modules/db.md](modules/db.md) | Cómo funciona la base de datos |

---

## 📂 Orden de lectura recomendado

Sigue este orden cuando explores el código con Álvaro:

1. **[README.md](../README.md)** — qué es el proyecto y cómo arrancarlo
2. **[abstract_lifemanager.py](../src/core/interfaces/abstract_lifemanager.py)** — la clase abstracta
3. **[memory_lifemanager.py](../src/core/impl/memory_lifemanager.py)** — la implementación más simple (fácil de leer)
4. **[sqlite_lifemanager.py](../src/core/impl/sqlite_lifemanager.py)** — la implementación real
5. **[models.py](../src/db/models.py)** — las tablas como clases
6. **[appointments.py](../src/api/routers/appointments.py)** — los endpoints de la API
7. **[api_client.py](../src/bot/api_client.py)** — el bot hablando con la API
8. **[handlers.py](../src/bot/handlers.py)** — los comandos del bot (el más grande, 60KB)

---

*Álvaro Fernández Mota · Abril 2026*
