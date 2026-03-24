# THDORA — Dockerfile
# Fase 10: Docker + Deploy

FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copiar código fuente
COPY src/ ./src/

# Ejecutar API por defecto
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
