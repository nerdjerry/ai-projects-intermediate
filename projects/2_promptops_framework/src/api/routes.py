"""API routes for prompt management and evaluation.

This module exposes endpoints for evaluating prompt outputs against references
using pluggable metrics, and for managing versioned prompt templates.

Design principles:
  - OCP: New metrics are added to METRIC_REGISTRY without modifying endpoints.
  - SRP: Each endpoint delegates to a focused service (evaluator or store).
  - DIP: Metrics are accessed through the abstract IMetric interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.evaluator import PromptEvaluator
from ..services.metrics import ExactMatchMetric, ContainsMetric, LengthRatioMetric
from ..services.prompt_store import PromptStore

router = APIRouter()

# --- Schemas ---


class EvaluateRequest(BaseModel):
    """Request schema for prompt evaluation.

    Attributes:
        predictions: List of model output strings to evaluate.
        references: List of expected reference strings (must match predictions length).
        metrics: Which metrics to compute (defaults to exact_match + contains).
    """
    predictions: list[str]
    references: list[str]
    metrics: list[str] = Field(default=["exact_match", "contains"])


class EvaluateResponse(BaseModel):
    """Response schema containing averaged metric scores."""
    scores: dict[str, float]


class SavePromptRequest(BaseModel):
    """Request schema for saving a new prompt version."""
    name: str
    template: str
    scores: dict[str, float] = Field(default_factory=dict)


class PromptVersionResponse(BaseModel):
    """Response schema for a prompt version."""
    template: str
    version: int
    scores: dict[str, float]


# --- Metric registry ---
# Add new metrics here to make them available via the API (OCP).
# Each metric implements the IMetric interface, so the evaluator
# doesn't need to know about specific metric implementations.

METRIC_REGISTRY = {
    "exact_match": ExactMatchMetric(),
    "contains": ContainsMetric(),
    "length_ratio": LengthRatioMetric(),
}

# --- Endpoints ---


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_prompt(req: EvaluateRequest) -> EvaluateResponse:
    """Evaluate predictions against references using selected metrics.

    Returns averaged scores for each requested metric. Raises HTTP 400
    if predictions and references have different lengths, or if no valid
    metrics are specified.
    """
    # Validate that predictions and references have matching lengths
    # before passing to the evaluator (prevents confusing 500 errors).
    if len(req.predictions) != len(req.references):
        raise HTTPException(
            status_code=400,
            detail=(
                f"predictions and references must have the same length, "
                f"got {len(req.predictions)} and {len(req.references)}"
            ),
        )

    selected = [METRIC_REGISTRY[m] for m in req.metrics if m in METRIC_REGISTRY]
    if not selected:
        raise HTTPException(status_code=400, detail="No valid metrics specified")
    evaluator = PromptEvaluator(metrics=selected)
    scores = evaluator.evaluate(req.predictions, req.references)
    return EvaluateResponse(scores=scores)


@router.post("/prompts", response_model=PromptVersionResponse)
async def save_prompt(req: SavePromptRequest) -> PromptVersionResponse:
    """Save a new prompt version with optional evaluation scores."""
    store = PromptStore()
    pv = store.save(req.name, req.template, req.scores)
    return PromptVersionResponse(template=pv.template, version=pv.version, scores=pv.scores)


@router.get("/prompts/{name}", response_model=list[PromptVersionResponse])
async def list_prompt_versions(name: str) -> list[PromptVersionResponse]:
    """List all versions of a prompt, ordered chronologically."""
    store = PromptStore()
    versions = store.list_versions(name)
    if not versions:
        raise HTTPException(status_code=404, detail=f"No prompt '{name}' found")
    return [
        PromptVersionResponse(template=v.template, version=v.version, scores=v.scores)
        for v in versions
    ]


@router.get("/prompts/{name}/best")
async def get_best_prompt(name: str, metric: str = "exact_match") -> PromptVersionResponse:
    """Get the best-scoring version of a prompt for a given metric."""
    store = PromptStore()
    best = store.get_best(name, metric)
    if not best:
        raise HTTPException(status_code=404, detail=f"No prompt '{name}' found")
    return PromptVersionResponse(template=best.template, version=best.version, scores=best.scores)
