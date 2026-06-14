import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from agents.models import Agent, Tool, ConversationMessage, MessageRole


# ── Agents ──────────────────────────────────────────────────────────────────

async def get_agent(db: AsyncSession, agent_id: uuid.UUID) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def get_agent_with_tools(db: AsyncSession, agent_id: uuid.UUID) -> tuple[Agent | None, list[Tool]]:
    agent = await get_agent(db, agent_id)
    if agent is None:
        return None, []
    tools: list[Tool] = []
    if agent.active_tools:
        result = await db.execute(select(Tool).where(Tool.name.in_(agent.active_tools)))
        tools = list(result.scalars().all())
    return agent, tools


async def list_agents(db: AsyncSession, tenant_id: uuid.UUID | None = None) -> list[Agent]:
    stmt = select(Agent).where(Agent.is_active.is_(True))
    if tenant_id is not None:
        stmt = stmt.where(Agent.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_agent(db: AsyncSession, **kwargs) -> Agent:
    agent = Agent(**kwargs)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def update_agent(db: AsyncSession, agent_id: uuid.UUID, **kwargs) -> Agent | None:
    agent = await get_agent(db, agent_id)
    if agent is None:
        return None
    for key, value in kwargs.items():
        setattr(agent, key, value)
    agent.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent_id: uuid.UUID) -> bool:
    agent = await get_agent(db, agent_id)
    if agent is None:
        return False
    await db.delete(agent)
    await db.commit()
    return True


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_tool_by_name(db: AsyncSession, name: str) -> Tool | None:
    result = await db.execute(select(Tool).where(Tool.name == name))
    return result.scalar_one_or_none()


async def list_tools(db: AsyncSession) -> list[Tool]:
    result = await db.execute(select(Tool))
    return list(result.scalars().all())


async def register_tool(db: AsyncSession, **kwargs) -> Tool:
    tool = Tool(**kwargs)
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def delete_tool(db: AsyncSession, tool_name: str) -> bool:
    result = await db.execute(delete(Tool).where(Tool.name == tool_name))
    await db.commit()
    return result.rowcount > 0


# ── Conversation history ──────────────────────────────────────────────────────

async def save_message(
    db: AsyncSession,
    agent_id: uuid.UUID,
    chat_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict] = None,
) -> ConversationMessage:
    msg = ConversationMessage(
        agent_id=agent_id,
        chat_id=chat_id,
        role=role,
        content=content,
        tool_calls_json=tool_calls,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_history(
    db: AsyncSession,
    agent_id: uuid.UUID,
    chat_id: str,
    limit: int = 20,
) -> list[dict]:
    result = await db.execute(
        select(ConversationMessage)
        .where(
            ConversationMessage.agent_id == agent_id,
            ConversationMessage.chat_id == chat_id,
        )
        .order_by(ConversationMessage.created_at.asc())
        .limit(limit)
    )
    msgs = result.scalars().all()
    return [
        {
            "role": m.role.value,
            "content": m.content,
            **(({"tool_calls": m.tool_calls_json}) if m.tool_calls_json else {}),
        }
        for m in msgs
    ]
