"""FastAPI application for the Meeting Transcription System.

Sets up the application with proper lifecycle management for services.
Services (transcriber, diarizer, indexer, meeting service) are initialized
during app startup and stored in app.state for dependency injection.

This approach replaces module-level singletons, preventing unbounded memory
growth and making the app easier to test.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from ..services.in_memory_indexer import InMemoryIndexer
from ..services.meeting_service import MeetingService
from ..services.mock_diarizer import MockDiarizer
from ..services.mock_transcriber import MockTranscriber


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared services on startup, clean up on shutdown.

    The transcriber and diarizer are mock implementations for development.
    Swap them for real implementations (e.g., WhisperTranscriber, PyAnnoteDiarizer)
    by changing the classes instantiated here — no other code changes needed (DIP).
    """
    # Initialize services — swap mock implementations for real ones here
    indexer = InMemoryIndexer()
    app.state.indexer = indexer
    app.state.meeting_svc = MeetingService(
        transcriber=MockTranscriber(),
        diarizer=MockDiarizer(),
        indexer=indexer,
    )
    yield
    # Cleanup: clear the in-memory index on shutdown
    await indexer.clear()


app = FastAPI(
    title="Meeting Transcription System",
    description="Searchable meeting knowledge system — transcribe, diarize, query",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")
