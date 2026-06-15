# Deployment with Docker

To deploy THDORA in production or staging environments (servidor Madre).

## Prerequisites

```bash
# Copy env file
cp .env.example .env
# Edit with real values
nano .env
```

Required in `.env`:
```
TELEGRAM_TOKEN=your_token
GROQ_API_KEY=your_key
DATABASE_URL=sqlite:///data/thdora.db
```

## Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/bot/main.py"]
```

## Docker Compose

```yaml
services:
  thdora-bot:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  thdora-api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## Execution

```bash
# Build and start
docker compose up -d --build

# Check status
docker compose ps

# Logs
docker compose logs -f thdora-bot
docker compose logs -f thdora-api

# Stop
docker compose down
```

## Makefile shortcuts

```bash
make deploy    # build + up -d
make logs      # follow logs
make stop      # down
```
