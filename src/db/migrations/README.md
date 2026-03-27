# Migraciones Alembic — THDORA

Este directorio contendrá las migraciones de Alembic cuando se configure.

## Estado actual

F9 usa `Base.metadata.create_all()` al arrancar — crea las tablas automáticamente
sin necesidad de migraciones manuales.

Alembic se configurará en F9.1 cuando necesitemos migraciones incrementales
(añadir columnas, renombrar tablas, etc.).

## Setup futuro

```bash
pip install alembic
alembic init src/db/migrations
# editar alembic.ini con la URL de la BD
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
