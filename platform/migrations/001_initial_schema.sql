-- THDORA Agent Platform v2 — Schema inicial
-- Requiere: PostgreSQL 16+ con extensiones uuid-ossp y pgvector

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- TENANTS
-- ============================================================
CREATE TABLE IF NOT EXISTS tenants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_user_id BIGINT UNIQUE,
    name            VARCHAR(255),
    email           VARCHAR(255) UNIQUE,
    plan            VARCHAR(50) DEFAULT 'free',  -- free | pro | enterprise
    api_key         VARCHAR(128) UNIQUE,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AGENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS agents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    system_prompt   TEXT NOT NULL,
    model           VARCHAR(100) DEFAULT 'llama-3.3-70b-versatile',
    temperature     FLOAT DEFAULT 0.7,
    max_tokens      INTEGER DEFAULT 4096,
    active_tools    UUID[] DEFAULT '{}',
    embedding_model VARCHAR(100) DEFAULT 'nomic-embed-text',
    config          JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agents_tenant ON agents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agents_active_tools ON agents USING GIN(active_tools);

-- ============================================================
-- TOOLS — Registry dinámico
-- ============================================================
CREATE TABLE IF NOT EXISTS tools (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(100) UNIQUE NOT NULL,
    description         TEXT NOT NULL,
    json_schema         JSONB NOT NULL,       -- schema que ve el LLM
    implementation_ref  VARCHAR(255),         -- 'tools.calendar.create_event' o 'http://endpoint'
    category            VARCHAR(50),          -- calendar | crm | email | web | custom
    is_public           BOOLEAN DEFAULT true,
    tenant_id           UUID REFERENCES tenants(id) ON DELETE SET NULL,  -- NULL = global
    version             VARCHAR(20) DEFAULT '1.0',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_public ON tools(is_public);

-- ============================================================
-- MESSAGES — Historial por agente + embeddings (memoria)
-- ============================================================
CREATE TABLE IF NOT EXISTS agent_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id    UUID REFERENCES agents(id) ON DELETE CASCADE,
    chat_id     TEXT NOT NULL,               -- telegram chat_id u otro
    role        VARCHAR(20) NOT NULL,        -- user | assistant | tool
    content     TEXT,
    tool_calls  JSONB,
    embedding   vector(768),                 -- pgvector: memoria semántica
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_agent_chat ON agent_messages(agent_id, chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_embedding ON agent_messages USING ivfflat (embedding vector_cosine_ops);

-- ============================================================
-- SEEDS — Tools built-in
-- ============================================================
INSERT INTO tools (name, description, json_schema, implementation_ref, category, is_public)
VALUES
(
    'send_telegram_message',
    'Envía un mensaje de texto a un chat de Telegram',
    '{"type":"object","properties":{"chat_id":{"type":"string"},"text":{"type":"string"}},"required":["chat_id","text"]}',
    'tools.telegram.send_message',
    'telegram',
    true
),
(
    'schedule_reminder',
    'Programa un recordatorio para una fecha y hora específica',
    '{"type":"object","properties":{"chat_id":{"type":"string"},"message":{"type":"string"},"datetime":{"type":"string","format":"date-time"}},"required":["chat_id","message","datetime"]}',
    'tools.scheduler.create_reminder',
    'calendar',
    true
),
(
    'query_agent_memory',
    'Busca en la memoria semántica del agente para recuperar contexto relevante',
    '{"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer","default":5}},"required":["query"]}',
    'tools.memory.semantic_search',
    'memory',
    true
),
(
    'http_request',
    'Realiza una petición HTTP a una URL externa (GET o POST)',
    '{"type":"object","properties":{"url":{"type":"string"},"method":{"type":"string","enum":["GET","POST"]},"payload":{"type":"object"}},"required":["url","method"]}',
    'tools.http.request',
    'custom',
    true
)
ON CONFLICT (name) DO NOTHING;
