from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Agent, Tool, Tenant
from .schemas import AgentCreate, AgentUpdate, ToolCreate
from core.cache import invalidate_agent_cache


# ── Tenants ──────────────────────────────────────────────────
async def get_or_create_tenant(db: AsyncSession, telegram_user_id: int, name: str = "Usuario") -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.telegram_user_id == telegram_user_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(telegram_user_id=telegram_user_id, name=name)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
    return tenant


# ── Agents ───────────────────────────────────────────────────
async def create_agent(db: AsyncSession, tenant_id: UUID, data: AgentCreate) -> Agent:
    agent = Agent(
        tenant_id=tenant_id,
        **data.model_dump(exclude={"active_tools"}),
        active_tools=[str(t) for t in data.active_tools],
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_agent(db: AsyncSession, agent_id: UUID) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def list_agents(db: AsyncSession, tenant_id: UUID) -> list[Agent]:
    result = await db.execute(select(Agent).where(Agent.tenant_id == tenant_id, Agent.is_active == True))
    return result.scalars().all()


async def update_agent(db: AsyncSession, agent_id: UUID, data: AgentUpdate) -> Agent | None:
    agent = await get_agent(db, agent_id)
    if not agent:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(agent, field, value)
    await db.commit()
    await db.refresh(agent)
    await invalidate_agent_cache(str(agent_id))  # invalidar caché
    return agent


async def attach_tool_to_agent(db: AsyncSession, agent_id: UUID, tool_id: UUID) -> Agent | None:
    agent = await get_agent(db, agent_id)
    if not agent:
        return None
    tool_id_str = str(tool_id)
    if tool_id_str not in agent.active_tools:
        agent.active_tools = agent.active_tools + [tool_id_str]
    await db.commit()
    await db.refresh(agent)
    await invalidate_agent_cache(str(agent_id))
    return agent


async def get_agent_with_tools(db: AsyncSession, agent_id: UUID) -> tuple[dict, list[dict]]:
    """Devuelve config del agente + lista de configs de sus tools activos."""
    agent = await get_agent(db, agent_id)
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")

    tools = []
    if agent.active_tools:
        result = await db.execute(
            select(Tool).where(Tool.id.in_([UUID(t) for t in agent.active_tools]))
        )
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "json_schema": t.json_schema,
                "implementation_ref": t.implementation_ref,
            }
            for t in result.scalars().all()
        ]

    agent_data = {
        "id": str(agent.id),
        "name": agent.name,
        "system_prompt": agent.system_prompt,
        "model": agent.model,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "config": agent.config,
    }
    return agent_data, tools


# ── Tools ────────────────────────────────────────────────────
async def register_tool(db: AsyncSession, data: ToolCreate, tenant_id: UUID | None = None) -> Tool:
    tool = Tool(**data.model_dump(), tenant_id=tenant_id)
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def list_tools(db: AsyncSession, category: str | None = None, include_private: bool = False) -> list[Tool]:
    query = select(Tool).where(Tool.is_public == True)
    if category:
        query = query.where(Tool.category == category)
    result = await db.execute(query)
    return result.scalars().all()
