"""FastAPI application for the Synthetic Data Factory."""
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Synthetic Data Factory",
    description="Automated Q&A dataset generation pipeline",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
