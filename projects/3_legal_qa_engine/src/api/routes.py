"""
API routes for the Legal Q&A Engine.

This module defines the HTTP endpoints (routes) and their associated
request/response schemas using **FastAPI** and **Pydantic**.

**Architecture notes for learners:**

• **Pydantic models** (``BaseModel`` subclasses) serve as both
  documentation and runtime validation. FastAPI automatically
  validates incoming JSON against these schemas and returns a ``422``
  error when the payload is invalid — no manual validation code needed.

• **Separation of concerns:** Routes are thin controllers that
  delegate to service classes (``DatasetBuilder``). They do not contain
  business logic themselves, which keeps them easy to test and replace.

• **SOLID – Single Responsibility Principle (SRP):** Each endpoint
  does one thing (chunk, summarize, analyze risk, or answer a question).
  Each Pydantic model describes one request or response shape.

• **SOLID – Dependency Inversion Principle (DIP):** In a full
  deployment the endpoints would receive ``ISummarizer``, ``IQAEngine``,
  and ``IRiskAnalyzer`` via FastAPI's dependency injection system
  (``Depends``). The current placeholder implementations demonstrate
  the endpoint contracts without requiring an API key.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.dataset_builder import DatasetBuilder

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------
# Each schema is a Pydantic BaseModel. FastAPI uses these for:
#   1. Automatic request validation (type checking, constraints).
#   2. OpenAPI / Swagger documentation generation.
#   3. Response serialization.
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    """Schema for the ``/summarize`` endpoint request body."""
    text: str = Field(..., min_length=1, description="Legal text to summarize")
    max_length: int = Field(default=500, ge=50, le=2000)


class SummarizeResponse(BaseModel):
    """Schema for the ``/summarize`` endpoint response body."""
    summary: str


class RiskAnalysisRequest(BaseModel):
    """Schema for the ``/analyze-risk`` endpoint request body."""
    text: str = Field(..., min_length=1, description="Legal text to analyze")


class RiskFinding(BaseModel):
    """A single risk finding returned by the risk-analysis endpoint."""
    clause: str
    risk_level: str
    explanation: str


class RiskAnalysisResponse(BaseModel):
    """Schema for the ``/analyze-risk`` endpoint response body."""
    findings: list[RiskFinding]


class AskRequest(BaseModel):
    """Schema for the ``/ask`` endpoint request body."""
    question: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    """Schema for the ``/ask`` endpoint response body."""
    answer: str


class ChunkRequest(BaseModel):
    """Schema for the ``/chunk`` endpoint request body."""
    text: str = Field(..., min_length=1)
    max_chars: int = Field(default=1000, ge=100, le=5000)


class ClauseResponse(BaseModel):
    """Schema for each item in the ``/chunk`` endpoint response."""
    text: str
    label: str
    risk_level: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chunk", response_model=list[ClauseResponse])
async def chunk_and_label(req: ChunkRequest) -> list[ClauseResponse]:
    """Chunk text and label clauses with risk levels.

    This endpoint demonstrates the **DatasetBuilder** in action:
    it splits incoming text into paragraph-based chunks and labels
    each chunk with a risk level using keyword heuristics.

    No LLM is required — the heuristic labelling works offline.
    """
    builder = DatasetBuilder()
    chunks = builder.chunk_text(req.text, req.max_chars)
    clauses = [builder.label_clause(chunk) for chunk in chunks]
    return [
        ClauseResponse(text=c.text, label=c.label, risk_level=c.risk_level)
        for c in clauses
    ]


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """Summarize legal text (requires LLM — returns placeholder without API key).

    In a production deployment, this would inject an ``ISummarizer``
    implementation (via FastAPI ``Depends``) that delegates to an LLM.
    The placeholder response lets the API contract be tested without
    incurring LLM costs.
    """
    # Without an actual LLM configured, return a structural summary.
    word_count = len(req.text.split())
    return SummarizeResponse(
        summary=f"Document contains {word_count} words. Use with configured LLM for full summarization."
    )


@router.post("/analyze-risk", response_model=RiskAnalysisResponse)
async def analyze_risk(req: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """Analyze legal text for risks using heuristic labeling.

    Uses ``DatasetBuilder.label_clause`` to scan for high- and
    medium-risk keywords. Only clauses with a non-"low" risk level
    are included in the response, keeping the output focused on
    actionable findings.
    """
    builder = DatasetBuilder()
    chunks = builder.chunk_text(req.text)
    clauses = [builder.label_clause(chunk) for chunk in chunks]
    # Filter to only non-low-risk findings to reduce noise.
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
    """Answer a legal question (requires LLM — returns placeholder without API key).

    Like ``/summarize``, this endpoint would use an ``IQAEngine``
    implementation in production. The placeholder confirms that the
    request schema and routing work correctly.
    """
    return AskResponse(
        answer=f"Question received: '{req.question}'. Configure LLM for full answers."
    )
