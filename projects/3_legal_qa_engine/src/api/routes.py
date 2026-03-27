"""API routes for the Legal Q&A Engine."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.dataset_builder import DatasetBuilder

router = APIRouter()


# --- Schemas ---

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Legal text to summarize")
    max_length: int = Field(default=500, ge=50, le=2000)


class SummarizeResponse(BaseModel):
    summary: str


class RiskAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Legal text to analyze")


class RiskFinding(BaseModel):
    clause: str
    risk_level: str
    explanation: str


class RiskAnalysisResponse(BaseModel):
    findings: list[RiskFinding]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    answer: str


class ChunkRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_chars: int = Field(default=1000, ge=100, le=5000)


class ClauseResponse(BaseModel):
    text: str
    label: str
    risk_level: str


# --- Endpoints ---

@router.post("/chunk", response_model=list[ClauseResponse])
async def chunk_and_label(req: ChunkRequest) -> list[ClauseResponse]:
    """Chunk text and label clauses with risk levels."""
    builder = DatasetBuilder()
    chunks = builder.chunk_text(req.text, req.max_chars)
    clauses = [builder.label_clause(chunk) for chunk in chunks]
    return [
        ClauseResponse(text=c.text, label=c.label, risk_level=c.risk_level)
        for c in clauses
    ]


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """Summarize legal text (requires LLM — returns placeholder without API key)."""
    # Without an actual LLM configured, return a structural summary
    word_count = len(req.text.split())
    return SummarizeResponse(
        summary=f"Document contains {word_count} words. Use with configured LLM for full summarization."
    )


@router.post("/analyze-risk", response_model=RiskAnalysisResponse)
async def analyze_risk(req: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """Analyze legal text for risks using heuristic labeling."""
    builder = DatasetBuilder()
    chunks = builder.chunk_text(req.text)
    clauses = [builder.label_clause(chunk) for chunk in chunks]
    findings = [
        RiskFinding(
            clause=c.text[:200],
            risk_level=c.risk_level,
            explanation=f"Detected '{c.label}' keyword pattern",
        )
        for c in clauses
        if c.risk_level != "low"
    ]
    return RiskAnalysisResponse(findings=findings)


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest) -> AskResponse:
    """Answer a legal question (requires LLM — returns placeholder without API key)."""
    return AskResponse(
        answer=f"Question received: '{req.question}'. Configure LLM for full answers."
    )
