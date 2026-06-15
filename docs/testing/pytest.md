# Testing with Pytest

We use `pytest` for unit and integration testing.

## Setup

```bash
pip install pytest pytest-asyncio
```

Or via pyproject.toml (already included):
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific module
pytest tests/test_nlp_engine.py

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Example Unit Test

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_nlp_handler_extracts_user_id():
    """NLP handler must always extract user_id from update."""
    update = AsyncMock()
    update.effective_user.id = 123456789
    context = AsyncMock()

    with patch("src.bot.handlers.nlp.api") as mock_api:
        mock_api.get_summary = AsyncMock(return_value={})
        from src.bot.handlers.nlp import nlp_handler
        await nlp_handler(update, context)

    # user_id must be passed to every API call
    assert mock_api.get_summary.called
```

## Test Structure

```
tests/
├── test_api/
│   ├── test_appointments.py
│   ├── test_habits.py
│   └── test_summary.py
├── test_bot/
│   ├── test_nlp_handler.py
│   └── test_commands.py
└── test_core/
    └── test_sqlite_lifemanager.py
```
