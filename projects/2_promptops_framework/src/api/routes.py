"""API routes for prompt management and evaluation."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.evaluator import PromptEvaluator
from ..services.metrics import ExactMatchMetric, ContainsMetric, LengthRatioMetric
from ..services.prompt_store import PromptStore

router = APIRouter()

# --- Schemas ---

class EvaluateRequest(BaseModel):
    predictions: list[str]
    references: list[str]
    metrics: list[str] = Field(default=["exact_match", "contains"])


class EvaluateResponse(BaseModel):
    scores: dict[str, float]


class SavePromptRequest(BaseModel):
    name: str
    template: str
    scores: dict[str, float] = Field(default_factory=dict)


class PromptVersionResponse(BaseModel):
    template: str
    version: int
    scores: dict[str, float]


# --- Metric registry ---

METRIC_REGISTRY = {
    "exact_match": ExactMatchMetric(),
    "contains": ContainsMetric(),
    "length_ratio": LengthRatioMetric(),
}

# --- Endpoints ---

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_prompt(req: EvaluateRequest) -> EvaluateResponse:
    """Evaluate predictions against references."""
    selected = [METRIC_REGISTRY[m] for m in req.metrics if m in METRIC_REGISTRY]
    if not selected:
        raise HTTPException(status_code=400, detail="No valid metrics specified")
    evaluator = PromptEvaluator(metrics=selected)
    scores = evaluator.evaluate(req.predictions, req.references)
    return EvaluateResponse(scores=scores)


@router.post("/prompts", response_model=PromptVersionResponse)
async def save_prompt(req: SavePromptRequest) -> PromptVersionResponse:
    """Save a new prompt version."""
    store = PromptStore()
    pv = store.save(req.name, req.template, req.scores)
    return PromptVersionResponse(template=pv.template, version=pv.version, scores=pv.scores)


@router.get("/prompts/{name}", response_model=list[PromptVersionResponse])
async def list_prompt_versions(name: str) -> list[PromptVersionResponse]:
    """List all versions of a prompt."""
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
    """Get the best-scoring version of a prompt."""
    store = PromptStore()
    best = store.get_best(name, metric)
    if not best:
        raise HTTPException(status_code=404, detail=f"No prompt '{name}' found")
    return PromptVersionResponse(template=best.template, version=best.version, scores=best.scores)
