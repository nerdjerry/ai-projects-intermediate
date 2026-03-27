"""FastAPI application for the PromptOps Framework."""
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="PromptOps Framework",
    description="CI/CD for prompts — evaluate, version, optimize",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
