from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assistant import router as assistant_router
from app.api.cart import router as cart_router
from app.api.inventory import router as inventory_router
from app.api.products import router as products_router
from app.config import get_settings
from app.models.database import init_db, seed_default_catalog

settings = get_settings()

app = FastAPI(
    title="Agentic Shopping Assistant",
    version="1.0.0",
    description="Sample local shopping assistant using Python catalog, deterministic scoring, and optional LLM explanations.",
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(assistant_router)
app.include_router(inventory_router)
app.include_router(cart_router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    seed_default_catalog()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "ready": True}
