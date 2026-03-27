"""API routes for the Meeting Transcription System."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.in_memory_indexer import InMemoryIndexer
from ..services.meeting_service import MeetingService
from ..services.mock_diarizer import MockDiarizer
from ..services.mock_transcriber import MockTranscriber

router = APIRouter()

# --- Shared services ---
indexer = InMemoryIndexer()
meeting_svc = MeetingService(
    transcriber=MockTranscriber(),
    diarizer=MockDiarizer(),
    indexer=indexer,
)


# --- Schemas ---

class ProcessRequest(BaseModel):
    audio_path: str = Field(..., description="Path to audio file")


class ProcessResponse(BaseModel):
    segments: list[dict[str, Any]]
    action_items: list[dict[str, str]]
    indexed_count: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResponse(BaseModel):
    results: list[dict[str, Any]]


# --- Endpoints ---

@router.post("/process", response_model=ProcessResponse)
async def process_meeting(req: ProcessRequest) -> ProcessResponse:
    """Process an audio file: transcribe, diarize, extract actions, index."""
    result = await meeting_svc.process_meeting(req.audio_path)
    return ProcessResponse(**result)


@router.post("/search", response_model=SearchResponse)
async def search_transcripts(req: SearchRequest) -> SearchResponse:
    """Search across indexed meeting transcripts."""
    results = await indexer.search(req.query, top_k=req.top_k)
    if not results:
        return SearchResponse(results=[])
    return SearchResponse(results=results)


@router.get("/stats")
async def get_stats() -> dict[str, int]:
    """Get indexing statistics."""
    return {"indexed_documents": indexer.document_count}
