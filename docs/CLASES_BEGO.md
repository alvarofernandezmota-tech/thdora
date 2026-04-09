# 🐍 Clases, Atributos y Métodos — Guía Begoña

> Este documento es el siguiente paso después de los ejercicios.
> Aquí aprendes qué son las clases, los atributos y los métodos
> **usando código real de THDORA** como ejemplo.

---

## 🧠 ¿Qué es una clase?

Una **clase** es una plantilla para crear objetos.

Piensa en una clase como el molde de una galleta:
- El molde define la forma (← esto es la clase)
- Cada galleta que haces con ese molde es un objeto (← esto es la instancia)

```python
# Clase simple — la plantilla
class Persona:
    pass

# Crear objetos (instancias) a partir de la clase
bego  = Persona()
alvaro = Persona()
```

`bego` y `alvaro` son dos objetos distintos creados con la misma plantilla.

---

## 📦 Atributos — los datos del objeto

Los **atributos** son las variables que viven dentro de un objeto.
Se definen en el método especial `__init__` (el constructor).

```python
class Persona:
    def __init__(self, nombre, edad):   # constructor
        self.nombre = nombre            # atributo
        self.edad   = edad              # atributo

bego = Persona("Begoña", 25)
print(bego.nombre)   # → Begoña
print(bego.edad)     # → 25
```

`self` siempre es el primero — es la forma en que el objeto se refiere a sí mismo.

### Cómo se ve en THDORA — clase `Appointment`

En [`src/db/models.py`](../src/db/models.py) está la clase `Appointment`.
Cada atributo es una columna de la base de datos:

```python
class Appointment(Base):
    """Una cita del usuario."""
    __tablename__ = "appointments"   # nombre de la tabla en SQLite

    # ── ATRIBUTOS ─────────────────────────────────────────
    id:    int = columna(entero, clave_primaria=True)   # ID único
    date:  str = columna(texto, obligatorio=True)       # "2026-04-09"
    time:  str = columna(texto, obligatorio=True)       # "10:00"
    name:  str = columna(texto, obligatorio=True)       # "Médico"
    type:  str = columna(texto, por_defecto="otra")     # tipo de cita
    notes: str = columna(texto, opcional=True)          # notas extra
    index: int = columna(entero, por_defecto=0)         # número del día
```

Cuando creas una cita en el bot, THDORA hace esto por dentro:
```python
cita = Appointment(
    date  = "2026-04-09",
    time  = "10:00",
    name  = "Médico",
    type  = "salud",
    notes = "llevar analítica"
)
# cita es un objeto de la clase Appointment
# cita.date   → "2026-04-09"
# cita.name   → "Médico"
```

📂 **Archivo real:** [`src/db/models.py`](../src/db/models.py)

---

## ⚙️ Métodos — las funciones del objeto

Los **métodos** son funciones que pertenecen a una clase.
Siempre tienen `self` como primer parámetro.

```python
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad   = edad

    # ── MÉTODOS ──────────────────────────────
    def saludar(self):
        print(f"¡Hola! Me llamo {self.nombre}.")

    def es_mayor(self):
        return self.edad >= 18

bego = Persona("Begoña", 25)
bego.saludar()          # → ¡Hola! Me llamo Begoña.
print(bego.es_mayor())  # → True
```

### Cómo se ve en THDORA — método `to_dict()`

Cada clase de `models.py` tiene un método `to_dict()` que convierte el objeto en un diccionario.
Así la API puede devolverlo como JSON:

```python
class Appointment(Base):
    # ... atributos ...

    # ── MÉTODO ─────────────────────────────────
    def to_dict(self) -> dict:
        """Convierte la cita en un diccionario."""
        return {
            "id":    self.id,
            "date":  self.date,
            "time":  self.time,
            "name":  self.name,
            "type":  self.type,
            "notes": self.notes,
            "index": self.index,
        }

# Uso:
cita = Appointment(date="2026-04-09", time="10:00", name="Médico", type="salud")
print(cita.to_dict())
# → {"id": 1, "date": "2026-04-09", "time": "10:00", "name": "Médico", ...}
```

📂 **Archivo real:** [`src/db/models.py`](../src/db/models.py)

---

## 📋 Las tres clases de models.py

En THDORA hay tres clases de datos. Cada una es una tabla de la base de datos:

### `Appointment` — Cita

```
Clase: Appointment
├── Atributos
│   ├── id      → número único de la cita
│   ├── date    → "2026-04-09"
│   ├── time    → "10:00"
│   ├── name    → "Médico"
│   ├── type    → "salud"
│   ├── notes   → "llevar analítica"
│   └── index   → 1 (primera cita del día)
└── Métodos
    └── to_dict() → devuelve diccionario
```

### `Habit` — Hábito del día

```
Clase: Habit
├── Atributos
│   ├── id     → número único
│   ├── date   → "2026-04-09"
│   ├── habit  → "sueno"
│   └── value  → "8h"
└── Métodos
    └── to_dict() → devuelve diccionario
```

### `HabitConfig` — Configuración de cada hábito

```
Clase: HabitConfig
├── Atributos
│   ├── id          → número único
│   ├── name        → "sueno"
│   ├── habit_type  → "time" (numeric | time | boolean | text)
│   ├── unit        → "h" (horas)
│   ├── min_val     → 0.0
│   ├── max_val     → 24.0
│   ├── quick_vals  → "6h,7h,8h,9h" (botones rápidos)
│   └── xp_rule     → "gte:7" (da XP si duermes 7h+)
└── Métodos
    └── to_dict() → devuelve diccionario con quick_vals como lista
```

📂 **Archivo real:** [`src/db/models.py`](../src/db/models.py)

---

## 📐 Herencia — una clase que hereda de otra

La herencia permite que una clase hija **reutilice** el código de una clase madre
y lo extienda o cambie.

```python
# Clase madre
class Animal:
    def __init__(self, nombre):
        self.nombre = nombre

    def hablar(self):
        print("...")

# Clase hija — hereda de Animal
class Perro(Animal):
    def hablar(self):           # sobreescribe el método
        print("Guau!")

class Gato(Animal):
    def hablar(self):           # sobreescribe el método
        print("Miau!")

perro = Perro("Rex")
perro.hablar()   # → Guau!
print(perro.nombre)  # → Rex  (heredado de Animal)
```

### Cómo se ve en THDORA — `AbstractLifeManager`

En THDORA la clase madre define el **contrato** (qué tiene que poder hacer).
Las clases hijas deciden **cómo** hacerlo:

```python
# src/core/interfaces/abstract_lifemanager.py
from abc import ABC, abstractmethod

class AbstractLifeManager(ABC):     # ABC = clase abstracta, no se puede instanciar sola

    @abstractmethod                 # obliga a las hijas a implementar esto
    def create_appointment(self, date, time, name, type, notes=""):
        pass

    @abstractmethod
    def get_appointments(self, date):
        pass

    @abstractmethod
    def log_habit(self, date, habit, value):
        pass
```

Y las tres implementaciones heredan de ella:

```python
# src/core/impl/memory_lifemanager.py  ← más fácil de leer
class MemoryLifeManager(AbstractLifeManager):
    def __init__(self):
        self._appointments = {}   # diccionario en memoria
        self._habits = {}

    def create_appointment(self, date, time, name, type, notes=""):
        # guarda en el diccionario de memoria
        if date not in self._appointments:
            self._appointments[date] = []
        self._appointments[date].append({
            "time": time, "name": name, "type": type, "notes": notes
        })

    def get_appointments(self, date):
        return self._appointments.get(date, [])

# src/core/impl/sqlite_lifemanager.py  ← la real, guarda en base de datos
class SqliteLifeManager(AbstractLifeManager):
    def __init__(self, db_url):
        self.session_factory = crear_sesion(db_url)

    def create_appointment(self, date, time, name, type, notes=""):
        # guarda en SQLite
        with self.session_factory() as session:
            cita = Appointment(date=date, time=time, name=name, type=type, notes=notes)
            session.add(cita)
            session.commit()
```

Las dos cumplen el mismo contrato — tienen los mismos métodos —
pero cada una los implementa de forma distinta.

📂 **Archivos:**
- [`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py)
- [`src/core/impl/memory_lifemanager.py`](../src/core/impl/memory_lifemanager.py) ← **empieza por esta**
- [`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py)

---

## 🔍 Resumen visual — Clase, Atributo, Método

```
            CLASS
         ┌────────────────────────────┐
         │   class Appointment:       │
         ├────────────────────────────┤
ATRIBUTOS│   id, date, time, name...   │ ← datos
         ├────────────────────────────┤
MÉTODOS  │   def to_dict(self): ...   │ ← acciones
         └────────────────────────────┘

INSTANCIA (objeto creado):
   cita = Appointment(date="2026-04-09", time="10:00", name="Médico")
   cita.name       ← accede a un atributo
   cita.to_dict()  ← llama a un método
```

---

## 📊 El orden para aprender estas clases en THDORA

1. **[`src/db/models.py`](../src/db/models.py)**
   Clases simples con atributos y `to_dict()`. El mejor punto de entrada.
   Ver `Appointment` primero, luego `Habit`, luego `HabitConfig`.

2. **[`src/core/impl/memory_lifemanager.py`](../src/core/impl/memory_lifemanager.py)**
   Clase que usa diccionarios en memoria. Sin base de datos, fácil de leer.
   Aquí se ve `__init__` con `self._appointments = {}` y métodos que lo usan.

3. **[`src/core/interfaces/abstract_lifemanager.py`](../src/core/interfaces/abstract_lifemanager.py)**
   La clase abstracta: qué es `ABC`, qué hace `@abstractmethod`.
   Aquí se ve qué significa "contrato" en Python.

4. **[`src/core/impl/sqlite_lifemanager.py`](../src/core/impl/sqlite_lifemanager.py)**
   La implementación real. Usa `Appointment` y `Habit` de `models.py`.
   Aquí se conectan las capas.

5. **[`src/bot/api_client.py`](../src/bot/api_client.py)**
   Clase que habla con la API. Ejemplo de clase con métodos `async`.

---

## 🧩 Para practicar después

Después de ver estas clases, puedes crear una versión simple tú sola:

```python
# Crea una clase Tarea con:
#   Atributos: titulo, completada (bool), prioridad (1-3)
#   Métodos:
#     completar()  → pone completada = True
#     to_dict()    → devuelve diccionario
#     __str__()    → devuelve texto para print()

class Tarea:
    def __init__(self, titulo, prioridad=2):
        self.titulo     = ___
        self.completada = ___      # empieza en False
        self.prioridad  = ___

    def completar(self):
        self.completada = ___

    def to_dict(self):
        return {
            "titulo":     ___,
            "completada": ___,
            "prioridad":  ___,
        }

    def __str__(self):
        estado = "✅" if self.completada else "⏳"
        return f"{estado} [{self.prioridad}] {self.titulo}"


# Prueba:
t1 = Tarea("Estudiar Python", prioridad=1)
t2 = Tarea("Hacer ejercicio")

print(t1)            # → ⏳ [1] Estudiar Python
t1.completar()
print(t1)            # → ✅ [1] Estudiar Python
print(t1.to_dict())  # → {"titulo": "Estudiar Python", "completada": True, "prioridad": 1}
```

---

*Álvaro Fernández Mota · Abril 2026*
