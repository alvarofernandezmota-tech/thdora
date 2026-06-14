from fastapi import Header, HTTPException, status
from core.config import settings


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Dependencia FastAPI: valida el header X-API-Key contra settings.platform_api_key."""
    if x_api_key != settings.platform_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide a valid X-API-Key header.",
        )
    return x_api_key
