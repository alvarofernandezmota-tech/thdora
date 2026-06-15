# Troubleshooting

Common issues and solutions for the THDORA platform.

## Database (SQLite/SQLAlchemy)

**Error**: `sqlite3.OperationalError: no such table`
- **Fix**: Ensure your migrations are applied or the base model initialization is called:
  ```python
  from app.database import engine, Base
  Base.metadata.create_all(bind=engine)
  ```

**Error**: `database is locked`
- **Fix**: You are likely performing concurrent writes. Ensure SQLAlchemy session scope is handled per request.

## NLP & API (Groq)

**Error**: `APIConnectionError`
- **Fix**: Check your `GROQ_API_KEY` in `.env`.

**Error**: `RateLimitError`
- **Fix**: Implement exponential backoff in the agent handler. See `src/ai/groq_client.py` for the retry logic with tenacity.

## Telegram Bot

**Error**: `Conflict: Terminated by other getUpdates request`
- **Fix**: Stop any other running instances of the bot using the same API token.

```bash
# Find and kill other instances
ps aux | grep 'python.*bot'
kill <PID>
```

**Error**: Bot no responde
- **Fix**: Verifica que `TELEGRAM_TOKEN` esté en `.env` y que el servidor tenga acceso a internet.

```bash
# Test conexión Telegram
curl https://api.telegram.org/bot<TOKEN>/getMe
```
