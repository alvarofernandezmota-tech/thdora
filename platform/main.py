from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from api.endpoints.agents import router as agents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version} iniciando...")
    yield
    # Shutdown
    print("🛑 Cerrando plataforma...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema Operativo de Agentes IA — Multi-tenant, Tool Registry dinámico, LangGraph",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}
