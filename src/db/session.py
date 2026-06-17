"""
src/db/session.py — helpers de sesión SQLAlchemy.
Provee get_db como context manager (usado en middleware y código sync)
y como generador para FastAPI Depends.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from src.db.base import SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager: úsalo con `with get_db() as db:`"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_dep() -> Generator[Session, None, None]:
    """Generador para FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
