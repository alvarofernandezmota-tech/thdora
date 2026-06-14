from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from agents.schemas import AgentCreate, AgentUpdate, AgentOut, ChatRequest, ChatResponse, ToolCreate, ToolOut
from agents.crud import create_agent, get_agent, list_agents, update_agent, attach_tool_to_agent, register_tool, list_tools
from agents.orchestrator import get_orchestrator

router = APIRouter(prefix="/api", tags=["agents"])

# TODO: reemplazar por JWT real
DEFAULT_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


# ── Agents CRUD ──────────────────────────────────────────────
@router.post("/agents/", response_model=AgentOut, status_code=201)
async def create_new_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    return await create_agent(db, DEFAULT_TENANT_ID, data)


@router.get("/agents/", response_model=list[AgentOut])
async def get_my_agents(db: AsyncSession = Depends(get_db)):
    return await list_agents(db, DEFAULT_TENANT_ID)


@router.get("/agents/{agent_id}", response_model=AgentOut)
async def get_agent_by_id(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    agent = await get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return agent


@router.patch("/agents/{agent_id}", response_model=AgentOut)
async def update_agent_config(
    agent_id: UUID, data: AgentUpdate, db: AsyncSession = Depends(get_db)
):
    agent = await update_agent(db, agent_id, data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return agent


@router.post("/agents/{agent_id}/tools/attach")
async def attach_tool(
    agent_id: UUID, tool_id: UUID, db: AsyncSession = Depends(get_db)
):
    agent = await attach_tool_to_agent(db, agent_id, tool_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente o tool no encontrado")
    return {"status": "ok", "active_tools": agent.active_tools}


# ── Chat endpoint ────────────────────────────────────────────
@router.post("/chat/{agent_id}", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: UUID,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    agent = await get_agent(db, agent_id)
    if not agent or not agent.is_active:
        raise HTTPException(status_code=404, detail="Agente no encontrado o inactivo")

    orchestrator = await get_orchestrator(str(agent_id), db)
    result = await orchestrator.chat(
        message=request.message,
        chat_id=request.chat_id,
    )

    # Guardar historial (simplificado)
    from agents.models import AgentMessage  # noqa — se añade en siguiente fase

    return ChatResponse(
        agent_id=agent_id,
        chat_id=request.chat_id,
        reply=result["reply"],
        tool_calls_made=result["tool_calls_made"],
    )


# ── Tool Registry ────────────────────────────────────────────
@router.post("/tools/", response_model=ToolOut, status_code=201)
async def register_new_tool(data: ToolCreate, db: AsyncSession = Depends(get_db)):
    return await register_tool(db, data)


@router.get("/tools/", response_model=list[ToolOut])
async def list_available_tools(
    category: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    return await list_tools(db, category=category)
