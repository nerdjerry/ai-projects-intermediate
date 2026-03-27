"""API routes for the Meeting Transcription System.

This module defines endpoints for processing meeting audio files (transcribe,
diarize, extract action items, index) and searching across indexed transcripts.

Design principles:
  - DIP: Services are injected via FastAPI's dependency injection system,
    making them easily swappable for testing or production implementations.
  - SRP: Routes handle HTTP concerns only; business logic lives in services.
  - LSP: Any ITranscriber/IDiarizer/IIndexer implementation can be used.

Note on dependency injection:
  Services are initialized during app lifespan and stored in app.state.
  This replaces module-level singletons, giving explicit lifecycle control
  and preventing unbounded memory growth from orphaned state.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..services.in_memory_indexer import InMemoryIndexer
from ..services.meeting_service import MeetingService

router = APIRouter()


# --- Schemas ---


class ProcessRequest(BaseModel):
    """Request schema for processing a meeting audio file."""
    audio_path: str = Field(..., description="Path to audio file to process")


class ProcessResponse(BaseModel):
    """Response with transcription segments, action items, and index count."""
    segments: list[dict[str, Any]]
    action_items: list[dict[str, str]]
    indexed_count: int


class SearchRequest(BaseModel):
    """Request schema for searching indexed meeting transcripts."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Max results to return")


class SearchResponse(BaseModel):
    """Response containing search results from indexed transcripts."""
    results: list[dict[str, Any]]


# --- Dependency injection helpers ---
# Retrieve service instances from app.state (initialized during lifespan).


def get_indexer(request: Request) -> InMemoryIndexer:
    """Retrieve the indexer from app state (DIP)."""
    return request.app.state.indexer


def get_meeting_svc(request: Request) -> MeetingService:
    """Retrieve the meeting service from app state (DIP)."""
    return request.app.state.meeting_svc


# --- Endpoints ---


@router.post("/process", response_model=ProcessResponse)
async def process_meeting(
    req: ProcessRequest,
    meeting_svc: MeetingService = Depends(get_meeting_svc),
) -> ProcessResponse:
    """Process an audio file: transcribe, diarize, extract actions, index.

    This runs the full meeting processing pipeline:
    1. Transcribe audio into text segments
    2. Identify speakers via diarization
    3. Extract action items from the transcript
    4. Index segments for later search
    """
    result = await meeting_svc.process_meeting(req.audio_path)
    return ProcessResponse(**result)


@router.post("/search", response_model=SearchResponse)
async def search_transcripts(
    req: SearchRequest,
    indexer: InMemoryIndexer = Depends(get_indexer),
) -> SearchResponse:
    """Search across indexed meeting transcripts by keyword.

    Returns the top_k most relevant transcript segments matching the query.
    """
    results = await indexer.search(req.query, top_k=req.top_k)
    if not results:
        return SearchResponse(results=[])
    return SearchResponse(results=results)


@router.get("/stats")
async def get_stats(
    indexer: InMemoryIndexer = Depends(get_indexer),
) -> dict[str, int]:
    """Get indexing statistics (number of indexed documents)."""
    return {"indexed_documents": indexer.document_count}
