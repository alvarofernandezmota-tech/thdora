# 🐍 De los ejercicios a un proyecto real — Guía para Begoña

> Este documento conecta lo que has aprendido en [`ejerciciosbego`](https://github.com/alvarofernandezmota-tech/ejerciciosbego)
> con cómo está construido THDORA, un proyecto Python real.
>
> Cada sección te dice: *"esto que aprendiste en el ejercicio X, aquí es donde se usa"*.

---

## 🗺️ El mapa de THDORA

```
thdora/
├── src/
│   ├── api/              ← FastAPI: la "ventanilla" que recibe peticiones
│   │   └── routers/      ← appointments.py, habits.py, summary.py
│   ├── bot/              ← El bot de Telegram (lo que ves en el móvil)
│   │   ├── handlers.py   ← Una función por cada comando (/nueva, /citas…)
│   │   └── api_client.py ← Habla con la API
│   ├── core/
│   │   ├── interfaces/   ← La "plantilla" abstracta (clase madre)
│   │   │   └── abstract_lifemanager.py
│   │   └── impl/         ← Las implementaciones concretas (clases hijas)
│   │       ├── sqlite_lifemanager.py   ← la que usamos en producción
│   │       ├── json_lifemanager.py
│   │       └── memory_lifemanager.py  ← la que usamos en tests
│   └── db/               ← Base de datos SQLite
│       ├── models.py      ← Tablas de la BD como clases Python
│       └── base.py        ← Conexión a la BD
└── docs/                 ← Documentación (estás aquí)
```

---

## 📚 Ejercicio 01 → Variables

En el ejercicio aprendiste que una variable guarda un valor:
```python
nombre = "Begoña"
edad   = 25
```

En THDORA las variables guardan configuración del sistema.
Por ejemplo en `.env.example`:
```
TELEGRAM_BOT_TOKEN=tu_token_aqui
THDORA_API_URL=http://localhost:8000
THDORA_DB_URL=sqlite:///data/thdora.db
```
Cada línea es una variable de entorno — lo mismo que aprendiste, pero el valor viene de fuera del código para que sea seguro.

---

## 📚 Ejercicio 02 → Listas

En el ejercicio:
```python
frutas = ["manzana", "naranja", "plátano"]
```

En THDORA, cuando pides tus citas del día, la API devuelve una lista:
```python
# src/api/routers/appointments.py
citas = [
    {"time": "10:00", "type": "Médico",  "notes": "llevar analítica"},
    {"time": "17:00", "type": "Reunión", "notes": ""}
]
```
Es exactamente lo mismo — una lista con elementos — pero cada elemento es un diccionario con varios campos.

📂 **Dónde verlo:** [`src/api/routers/appointments.py`](../src/api/routers/appointments.py)

---

## 📚 Ejercicio 03 → Condiciones

En el ejercicio:
```python
if temperatura >= 30:
    print("Hace calor")
elif temperatura >= 20:
    print("Agradable")
```

En THDORA, el bot decide qué responder según el comando que escribes:
```python
# src/bot/handlers.py (simplificado)
if opcion == "/nueva":
    # flujo para crear cita
elif opcion == "/citas":
    # flujo para ver citas
elif opcion == "/cancelar":
    # cancela la operación
```
El bot es básicamente un if/elif gigante que reacciona a lo que escribes.

📂 **Dónde verlo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 04 → Bucles

En el ejercicio:
```python
for fruta in frutas:
    print(fruta)
```

En THDORA, cuando formateas el resumen del día, recorres la lista de citas con un for:
```python
# src/bot/handlers.py (simplificado)
for cita in citas:
    texto += f"🕐 {cita['time']} — {cita['type']}\n"
```
Mismo concepto: recorrer una lista y hacer algo con cada elemento.

📂 **Dónde verlo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 05 → Funciones

En el ejercicio:
```python
def saludar_a(nombre):
    print(f"¡Hola, {nombre}!")
```

En THDORA, cada comando del bot es una función. Por ejemplo:
```python
# src/bot/handlers.py (simplificado)
async def cmd_start(update, context):
    """Responde al comando /start con el mensaje de bienvenida."""
    await update.message.reply_text("¡Hola! Soy THDORA 🧠")

async def cmd_nueva(update, context):
    """Inicia el flujo de creación de una nueva cita."""
    await update.message.reply_text("¿Para qué fecha es la cita?")
```

Diferencias con tus ejercicios:
- `async` → la función puede esperar sin bloquear (Telegram es lento a veces)
- `update, context` → parámetros que Telegram pasa automáticamente
- `"""docstring"""` → descripción de lo que hace la función

📂 **Dónde verlo:** [`src/bot/handlers.py`](../src/bot/handlers.py)

---

## 📚 Ejercicio 05b → Menú con centinela

En el ejercicio hiciste un menú de bar donde `0` era el centinela para salir.

En THDORA, el bot también tiene un sistema de "salir del flujo":
```python
# Si el usuario escribe /cancelar en cualquier momento
async def cmd_cancelar(update, context):
    """Cancela cualquier operación en curso — es el centinela del bot."""
    return ConversationHandler.END   # ← equivalente al break
```

El `ConversationHandler.END` es exactamente el mismo concepto que tu `break` — para el flujo y vuelve al estado inicial.

---

## 🆕 Lo nuevo: Clases

Después de los ejercicios, el siguiente paso es **clases** — que son como una plantilla para crear objetos con sus propios datos y funciones.

### La clase abstracta — el contrato

```python
# src/core/interfaces/abstract_lifemanager.py
from abc import ABC, abstractmethod

class AbstractLifeManager(ABC):
    """
    Esta clase define QUÉ tiene que poder hacer un gestor de vida.
    NO dice CÓMO hacerlo — eso lo decide cada implementación.
    """

    @abstractmethod
    def create_appointment(self, date, time, type, notes=""):
        """Crea una cita. Obligatorio implementar."""
        pass

    @abstractmethod
    def get_appointments(self, date):
        """Devuelve las citas de un día. Obligatorio implementar."""
        pass

    @abstractmethod
    def log_habit(self, date, habit, value):
        """Registra un hábito. Obligatorio implementar."""
        pass
```

Es como un **contrato**: cualquier clase que herede de esta DEBE tener todos estos métodos.

📂 **Dónde verlo:** [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py)

---

### La clase concreta — la implementación real

```python
# src/core/impl/sqlite_lifemanager.py (simplificado)
from src.core.interfaces import AbstractLifeManager

class SqliteLifeManager(AbstractLifeManager):
    """
    Implementación que guarda los datos en SQLite.
    Hereda de AbstractLifeManager y cumple el contrato.
    """

    def __init__(self, db_url):
        """Constructor — se ejecuta al crear el objeto."""
        self.db_url = db_url
        self.session = crear_conexion(db_url)

    def create_appointment(self, date, time, type, notes=""):
        """Guarda la cita en la base de datos SQLite."""
        cita = AppointmentModel(date=date, time=time, type=type, notes=notes)
        self.session.add(cita)
        self.session.commit()
        return cita.id

    def get_appointments(self, date):
        """Lee las citas del día desde SQLite."""
        return self.session.query(AppointmentModel).filter_by(date=date).all()
```

Fíjate:
- `class SqliteLifeManager(AbstractLifeManager)` → hereda de la clase madre
- `def __init__(self, ...)` → constructor, como cuando hacías `lista = []`
- `self.` → guarda datos dentro del propio objeto

📂 **Dónde verlo:** [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py)

---

## 🔗 El flujo completo de una cita

Cuando escribes `/nueva` en Telegram:

```
Tú (Telegram)
    ↓  escribe /nueva
handlers.py          → función cmd_nueva()        [Ejercicio 05 — funciones]
    ↓  pregunta fecha, hora, tipo…
handlers.py          → recoge respuestas           [Ejercicio 03 — condiciones]
    ↓  llama a la API
api_client.py        → POST /appointments/{date}   [función que llama a la API]
    ↓
appointments.py      → router FastAPI              [recibe la petición]
    ↓
SqliteLifeManager    → create_appointment()        [clase — método]
    ↓
SQLite               → guarda en la base de datos
    ↓
Tú (Telegram)        ← "✅ Cita guardada"
```

Cada capa hace una cosa. Eso es arquitectura limpia.

---

## 📂 Archivos para ver en orden

1. [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py) — la clase abstracta
2. [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py) — cómo se implementa
3. [`src/db/models.py`](../src/db/models.py) — cómo son las tablas como clases
4. [`src/api/routers/appointments.py`](../src/api/routers/appointments.py) — los endpoints
5. [`src/bot/handlers.py`](../src/bot/handlers.py) — los comandos del bot

---

_Álvaro Fernández Mota · Abril 2026_
