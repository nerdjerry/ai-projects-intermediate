"""FastAPI application for the Meeting Transcription System."""
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Meeting Transcription System",
    description="Searchable meeting knowledge system — transcribe, diarize, query",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
