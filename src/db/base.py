"""
Engine y sesión SQLAlchemy para THDORA.

Usa SQLite por defecto (archivo local `thdora.db`).
La ruta se puede sobreescribir con la variable de entorno
``THDORA_DB_URL``.

Uso::

    from src.db.base import get_session

    with get_session() as session:
        session.add(appointment)
        session.commit()
"""

import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# URL de la base de datos — SQLite local por defecto
_DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "thdora.db"
DB_URL = os.environ.get("THDORA_DB_URL", f"sqlite:///{_DEFAULT_DB}")

# Crear directorio data/ si no existe
_DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},  # necesario para SQLite con async
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base declarativa compartida por todos los modelos ORM."""
    pass


@contextmanager
def get_session() -> Session:  # type: ignore[misc]
    """Context manager que provee una sesión y hace rollback en caso de error."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Crea todas las tablas si no existen. Llamar al arrancar la app."""
    from src.db import models  # noqa: F401 — registrar modelos en Base
    Base.metadata.create_all(bind=engine)
