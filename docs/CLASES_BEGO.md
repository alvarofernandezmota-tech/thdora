# 🐍 Clases, Atributos y Métodos — Guía Begoña

> Este documento es el siguiente paso después de los ejercicios.
> Cada ejemplo de código es **real** — está copiado exactamente del
> proyecto THDORA. Puedes abrir el archivo y ver la misma línea.

---

## ¿Qué es una clase?

Una **clase** es una plantilla para crear objetos.
Define qué datos tiene un objeto (atributos) y qué puede hacer (métodos).

Piensa en ello así:
- El molde de galleta = la clase
- Cada galleta = un objeto (instancia)

```python
# Esto es una clase simple:
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre   # atributo
        self.edad   = edad     # atributo

# Crear dos objetos (instancias) distintos:
bego   = Persona("Begoña", 25)
alvaro = Persona("Álvaro", 27)

print(bego.nombre)    # → Begoña
print(alvaro.nombre)  # → Álvaro
```

---

## Los tres conceptos clave

```
┌───────────────────────────────────────┐
│  class MemoryLifeManager:         │  ← CLASE
├───────────────────────────────────────┤
│  self.appointments = {}           │  ← ATRIBUTO (datos que guarda)
│  self.habits       = {}           │  ← ATRIBUTO
├───────────────────────────────────────┤
│  def create_appointment(...):     │  ← MÉTODO (cosas que sabe hacer)
│  def get_appointments(...):       │  ← MÉTODO
│  def log_habit(...):              │  ← MÉTODO
└───────────────────────────────────────┘
```

📂 Archivo real: [`src/core/impl/memory_lifemanager.py`](../src/core/impl/memory_lifemanager.py)

---

## Parte 1 — El constructor `__init__` y los atributos

El método especial `__init__` se ejecuta automáticamente cuando creas el objeto.
Aquí dentro se definen los atributos con `self.`.

### Código real de `MemoryLifeManager` — líneas 38–39

```python
# ▶ src/core/impl/memory_lifemanager.py

class MemoryLifeManager(AbstractLifeManager):
    """
    Gestor de vida personal con almacenamiento en memoria.

    Attributes:
        appointments (Dict[str, List[Dict]]): Citas indexadas por fecha.
        habits (Dict[str, Dict[str, str]]): Hábitos indexados por fecha.
    """

    def __init__(self) -> None:
        self.appointments: Dict[str, List[Dict]] = {}   # ← atributo: diccionario vacío
        self.habits: Dict[str, Dict[str, str]] = {}     # ← atributo: diccionario vacío
```

**Qué pasa al crear el objeto:**
```python
mgr = MemoryLifeManager()   # ← se ejecuta __init__
# Ahora mgr.appointments = {}
# Ahora mgr.habits       = {}
```

`Dict[str, List[Dict]]` es una anotación de tipo: dice que `appointments` es
un diccionario donde la clave es un string (la fecha) y el valor es una lista de diccionarios.
No cambia cómo funciona, sólo documenta qué tipo de dato espera.

---

## Parte 2 — Métodos con lógica real

Los métodos usan `self` para acceder a los atributos del propio objeto.

### Método `create_appointment` — líneas 43–74 (real)

```python
# ▶ src/core/impl/memory_lifemanager.py

def create_appointment(self, date: date, time: str, type: str, notes: str = "") -> UUID:
    """
    Crea una nueva cita y la almacena en memoria.
    """
    # 1. Valida que la hora tenga formato correcto (09:30, 23:00...)
    if not _TIME_RE.match(time):
        raise ValueError(
            f"Formato de hora inválido: '{time}'. Se espera HH:MM."
        )

    # 2. Valida que el tipo sea uno de los permitidos
    if type not in VALID_TYPES:
        raise ValueError(
            f"Tipo de cita inválido: '{type}'. "
            f"Valores permitidos: {sorted(VALID_TYPES)}"
        )

    # 3. Genera un ID único para la cita
    apt_id = uuid4()
    date_str = str(date)   # convierte date(2026,4,9) → "2026-04-09"

    # 4. Si es el primer día, crea la lista vacía
    if date_str not in self.appointments:     # ← accede al ATRIBUTO
        self.appointments[date_str] = []      # ← modifica el ATRIBUTO

    # 5. Añade la cita a la lista del día
    self.appointments[date_str].append({      # ← usa el ATRIBUTO
        "id": str(apt_id),
        "time": time,
        "type": type,
        "notes": notes,
    })

    return apt_id   # devuelve el ID para que el bot lo pueda usar
```

**Cómo se usa desde fuera:**
```python
from datetime import date

mgr = MemoryLifeManager()

cita_id = mgr.create_appointment(
    date(2026, 4, 9),   # fecha
    "10:00",            # hora
    "médica",           # tipo (debe ser de VALID_TYPES)
    "llevar analítica" # notas
)

print(cita_id)               # → UUID como 3f7a1b2c-...
print(mgr.appointments)      # → {"2026-04-09": [{"id":..., "time": "10:00", ...}]}
```

---

### Método `get_appointments` — línea 76 (real)

Este método es corto — sólo lee del atributo y devuelve la lista:

```python
# ▶ src/core/impl/memory_lifemanager.py

def get_appointments(self, date: date) -> List[Dict]:
    return self.appointments.get(str(date), [])   # si no existe, devuelve []
```

**Cómo se usa:**
```python
citas = mgr.get_appointments(date(2026, 4, 9))

for cita in citas:   # ← bucle del Ejercicio 04
    print(f"{cita['time']} — {cita['type']}")
# → 10:00 — médica
```

---

### Método `log_habit` — líneas 97–101 (real)

```python
# ▶ src/core/impl/memory_lifemanager.py

def log_habit(self, date: date, habit: str, value: str) -> bool:
    date_str = str(date)
    if date_str not in self.habits:       # si no existe el día...
        self.habits[date_str] = {}        # crea el diccionario vacío
    self.habits[date_str][habit] = value  # guarda el valor del hábito
    return True
```

**Cómo se usa:**
```python
mgr.log_habit(date(2026, 4, 9), "sueno", "8h")
mgr.log_habit(date(2026, 4, 9), "humor", "8")
mgr.log_habit(date(2026, 4, 9), "THC",   "0")

print(mgr.habits)
# → {"2026-04-09": {"sueno": "8h", "humor": "8", "THC": "0"}}
```

---

### Método `get_day_summary` — líneas 107–111 (real)

Este método llama a **otros métodos** del mismo objeto usando `self`:

```python
# ▶ src/core/impl/memory_lifemanager.py

def get_day_summary(self, date: date) -> Dict:
    return {
        "date":         str(date),
        "appointments": self.get_appointments(date),  # ← llama a otro método
        "habits":       self.get_habits(date),        # ← llama a otro método
    }
```

**Cómo se usa:**
```python
resumen = mgr.get_day_summary(date(2026, 4, 9))
print(resumen["date"])          # → "2026-04-09"
print(resumen["appointments"])  # → [{...}]
print(resumen["habits"])        # → {"sueno": "8h", ...}
```

---

## Parte 3 — Herencia: una clase que hereda de otra

`MemoryLifeManager` tiene `(AbstractLifeManager)` en su definición.
Eso significa que **hereda** de la clase madre.

### La clase madre — `AbstractLifeManager` (el contrato)

Está en [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py).
No guarda datos. Sólo **dice qué métodos deben existir** con `@abstractmethod`:

```python
# ▶ src/core/interfaces/abstract_lifemanager.py

from abc import ABC, abstractmethod

class AbstractLifeManager(ABC):    # ABC = no se puede instanciar sola

    @abstractmethod                # ← obliga a las hijas a implementar esto
    def create_appointment(self, date, time, type, notes=""):
        """
        Crea una nueva cita en el sistema.
        Toda implementación DEBE tener este método.
        """
        pass

    @abstractmethod
    def get_appointments(self, date):
        pass

    @abstractmethod
    def log_habit(self, date, habit, value):
        pass

    @abstractmethod
    def get_habits(self, date):
        pass

    @abstractmethod
    def get_day_summary(self, date):
        pass
```

Si intentas crear `AbstractLifeManager()` directamente, Python lanza un error.
Está diseñada sólo para ser heredada.

### La relación entre las clases

```
AbstractLifeManager   ← clase madre (contrato: qué debe poder hacerse)
        │
        ├─── MemoryLifeManager    ← guarda en diccionarios (RAM)
        ├─── JsonLifeManager      ← guarda en archivo .json  (pendiente)
        └─── SqliteLifeManager    ← guarda en SQLite (producción)
```

Las tres hijas tienen los mismos métodos pero los implementan de forma distinta.
El bot no sabe cuál está usando — sólo llama a `mgr.create_appointment(...)` y
funciona igual con cualquiera.

---

## Parte 4 — Clase `Appointment` en models.py

Además del LifeManager, THDORA tiene clases que representan las tablas de la base de datos.
Están en [`src/db/models.py`](../src/db/models.py).

```python
# ▶ src/db/models.py

class Appointment(Base):
    """Cita del usuario."""

    __tablename__ = "appointments"   # nombre de la tabla en SQLite

    # ATRIBUTOS = columnas de la tabla
    id:    int = mapped_column(Integer, primary_key=True, autoincrement=True)
    date:  str = mapped_column(String(10), nullable=False, index=True)  # "2026-04-09"
    time:  str = mapped_column(String(5),  nullable=False)              # "10:00"
    name:  str = mapped_column(String(200),nullable=False, default="")
    type:  str = mapped_column(String(50), nullable=False, default="otra")
    notes: str = mapped_column(Text, nullable=True)
    index: int = mapped_column(Integer,    nullable=False, default=0)

    # MÉTODO: convierte el objeto a diccionario
    def to_dict(self) -> dict:
        return {
            "id":    self.id,
            "date":  self.date,
            "time":  self.time,
            "name":  self.name,
            "type":  self.type,
            "notes": self.notes,
            "index": self.index,
        }
```

**Diferencia con `MemoryLifeManager`:**
- `MemoryLifeManager` → clase con lógica (sabe hacer cosas)
- `Appointment` → clase de datos (representa una fila de la base de datos)

Las dos son clases. Sólo tienen propósitos distintos.

---

## Flujo completo — cómo encajan las clases

Cuando escribes `/nueva` en Telegram y creas la cita "Médico 10:00":

```
Tú escribes "/nueva" en Telegram
    ↓
handlers.py → cmd_nueva()            ← función (Ejercicio 05)
    ↓ pregunta: fecha, hora, tipo...
handlers.py → recibir_tipo()         ← condiciones if/elif (Ejercicio 03)
    ↓ llama a la API
api_client.py → create_appointment() ← método de clase ApiClient
    ↓ POST /appointments/2026-04-09
appointments.py (router FastAPI)      ← recibe la petición HTTP
    ↓
SqliteLifeManager.create_appointment()
    → crea objeto Appointment(date=..., time=..., name=...) ← CLASE
    → session.add(cita)  ← guarda en SQLite
    → return cita.id
    ↓
"✅ Cita guardada para el 2026-04-09" ← respuesta al usuario
```

---

## Para practicar tú sola — ejercicio

Usa `MemoryLifeManager` como si fueras el bot:

```python
# Ejecuta esto en tu terminal o en un archivo .py
from datetime import date
from src.core.impl.memory_lifemanager import MemoryLifeManager

# 1. Crear el gestor
mgr = MemoryLifeManager()
print(mgr.appointments)   # → {}  (vacío)

# 2. Crear una cita
mgr.create_appointment(date(2026, 4, 9), "10:00", "médica", "llevar analítica")
mgr.create_appointment(date(2026, 4, 9), "17:00", "personal")
print(mgr.appointments)   # → {"2026-04-09": [{...}, {...}]}

# 3. Leer las citas del día
citas = mgr.get_appointments(date(2026, 4, 9))
for cita in citas:
    print(f"{cita['time']} — {cita['type']}")

# 4. Registrar hábitos
mgr.log_habit(date(2026, 4, 9), "sueno", "8h")
mgr.log_habit(date(2026, 4, 9), "humor", "9")

# 5. Ver el resumen del día
resumen = mgr.get_day_summary(date(2026, 4, 9))
print(resumen)
```

> 💡 Pista: `VALID_TYPES` acepta ``"médica"``, ``"personal"``, ``"trabajo"``, ``"otra"``

---

## Archivos del proyecto para abrir durante la clase

| Orden | Archivo | Por qué empezar aquí |
|-------|---------|----------------------|
| 1º | [`src/db/models.py`](../src/db/models.py) | Clases de datos simples — atributos y `to_dict()` |
| 2º | [`src/core/impl/memory_lifemanager.py`](../src/core/impl/memory_lifemanager.py) | Clase con lógica real, sin base de datos, fácil de leer |
| 3º | [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py) | La clase abstracta: herencia y contratos |
| 4º | [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py) | La implementación de producción: mismos métodos, SQLite real |

---

*Álvaro Fernández Mota · Abril 2026*
