"""FastAPI application for the Legal Q&A Engine."""
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Legal Q&A Engine",
    description="Domain-specialized legal LLM — summarize, analyze risk, ask questions",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
