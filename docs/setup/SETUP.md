# Guía de instalación y desarrollo

> Última actualización: 2026-03-25

## Requisitos

- Python 3.10+
- pip
- git

## Instalación

```bash
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
pip install -e .[dev]
```

## Ejecutar tests

```bash
# Todos los tests con coverage
pytest tests/ -v

# Solo unitarios
pytest tests/unit/ -v

# Solo integración
pytest tests/integration/ -v
```

## Ejecutar la API

```bash
uvicorn src.api.main:app --reload
```

Swagger UI disponible en: http://localhost:8000/docs

## Comandos Make

```bash
make test       # pytest con coverage
make lint       # ruff
make format     # black
make run        # uvicorn
```

## Estructura de datos

Los datos reales se guardan en `datos/thdora.json` (excluido de git).
Esta carpeta se crea automáticamente al primer uso.

## Variables de entorno

Actualmente no se requieren variables de entorno para el modo local.
Fase 7 (bot Telegram) requerirá `TELEGRAM_TOKEN`.
