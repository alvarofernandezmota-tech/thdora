import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.database import get_db
from core.auth import require_api_key
from agents import crud
from agents.orchestrator import get_orchestrator, invalidate_orchestrator_cache

router = APIRouter(prefix="/agents", tags=["agents"])

Auth = Annotated[str, Depends(require_api_key)]
DB = Annotated[AsyncSession, Depends(get_db)]


class AgentCreate(BaseModel):
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    system_prompt: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 4096
    active_tools: list[str] = []


class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    agent_id: str
    chat_id: str


@router.get("/")
async def list_agents(
    _: Auth,
    db: DB,
    tenant_id: uuid.UUID | None = None,
):
    agents = await crud.list_agents(db, tenant_id=tenant_id)
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "model": a.model,
            "is_active": a.is_active,
        }
        for a in agents
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(
    _: Auth,
    payload: AgentCreate,
    db: DB,
):
    agent = await crud.create_agent(db, **payload.model_dump())
    return {"id": str(agent.id), "name": agent.name}


@router.get("/{agent_id}")
async def get_agent(
    _: Auth,
    agent_id: uuid.UUID,
    db: DB,
):
    agent = await crud.get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "id": str(agent.id),
        "name": agent.name,
        "description": agent.description,
        "system_prompt": agent.system_prompt,
        "model": agent.model,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "active_tools": agent.active_tools,
        "is_active": agent.is_active,
    }


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    _: Auth,
    agent_id: uuid.UUID,
    db: DB,
):
    deleted = await crud.delete_agent(db, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    invalidate_orchestrator_cache(agent_id)


@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    _: Auth,
    agent_id: uuid.UUID,
    payload: ChatRequest,
    db: DB,
):
    orchestrator = await get_orchestrator(agent_id, db)
    if orchestrator is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    reply = await orchestrator.chat(
        user_message=payload.message,
        chat_id=payload.chat_id,
        db=db,
    )
    return ChatResponse(reply=reply, agent_id=str(agent_id), chat_id=payload.chat_id)
