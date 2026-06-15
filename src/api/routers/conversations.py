from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.api.models.conversation import Conversation

router = APIRouter(prefix="/conversations", tags=["conversations"])


class MessageIn(BaseModel):
    user_id: int
    role: str
    content: str
    session_id: str | None = None


@router.post("", status_code=201)
async def save_message(payload: MessageIn, db: Session = Depends(get_db)):
    entry = Conversation.save(
        db,
        user_id=payload.user_id,
        role=payload.role,
        content=payload.content,
        session_id=payload.session_id,
    )
    return {"id": entry.id, "timestamp": entry.timestamp.isoformat()}


@router.get("/{user_id}")
async def get_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    history = Conversation.get_history(db, user_id=user_id, limit=limit)
    return {"user_id": user_id, "history": history}


@router.delete("/{user_id}", status_code=204)
async def delete_history(user_id: int, db: Session = Depends(get_db)):
    deleted = (
        db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    )
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="No history found for this user")
