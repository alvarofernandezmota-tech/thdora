from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime


# ── Tenant ──────────────────────────────────────────────────
class TenantCreate(BaseModel):
    telegram_user_id: Optional[int] = None
    name: str
    email: Optional[str] = None
    plan: str = "free"


class TenantOut(TenantCreate):
    id: UUID
    api_key: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Agent ────────────────────────────────────────────────────
class AgentCreate(BaseModel):
    name: str
    description: str = ""
    system_prompt: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4096, ge=64, le=128000)
    active_tools: List[UUID] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    active_tools: Optional[List[UUID]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentOut(AgentCreate):
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Tool ─────────────────────────────────────────────────────
class ToolCreate(BaseModel):
    name: str
    description: str
    json_schema: Dict[str, Any]
    implementation_ref: Optional[str] = None
    category: str = "custom"
    is_public: bool = False


class ToolOut(ToolCreate):
    id: UUID
    version: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    chat_id: str                          # telegram chat_id u otro
    stream: bool = False


class ChatResponse(BaseModel):
    agent_id: UUID
    chat_id: str
    reply: str
    tool_calls_made: List[str] = []
    tokens_used: Optional[int] = None
