"""FastAPI application for the Personal Finance Agent."""
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Personal Finance Agent",
    description="Stateful AI agent with memory for personal finance",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
