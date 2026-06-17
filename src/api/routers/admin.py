"""
Router de administración — control de usuarios permitidos.
Requiere header X-Admin-Token == settings.ADMIN_TOKEN.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.bot.middleware import invalidate_allowed_users_cache
from src.config import settings
from src.db.models import AllowedUser

router = APIRouter(prefix="/admin", tags=["admin"])


class AllowedUserResponse(BaseModel):
    id: int
    user_id: int
    username: str | None
    added_at: str
    added_by: int | None


@router.post("/add_user", response_model=AllowedUserResponse, status_code=201)
def admin_add_user(
    user_id: int = Query(..., description="Telegram User ID a permitir"),
    username: str | None = Query(None, description="Username opcional"),
    added_by: int | None = Query(None, description="Admin que añade"),
    x_admin_token: str = Header(..., alias="X-Admin-Token"),
    db: Session = Depends(get_db),
) -> AllowedUserResponse:
    """Añade un usuario permitido. Requiere token de admin."""
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Token de administrador inválido")

    existing = db.query(AllowedUser).filter(AllowedUser.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"El usuario {user_id} ya está en la lista de permitidos."
        )

    new_user = AllowedUser(
        user_id=user_id,
        username=username,
        added_at=datetime.utcnow().isoformat(),
        added_by=added_by,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    invalidate_allowed_users_cache()

    return AllowedUserResponse(
        id=new_user.id,
        user_id=new_user.user_id,
        username=new_user.username,
        added_at=new_user.added_at,
        added_by=new_user.added_by,
    )
