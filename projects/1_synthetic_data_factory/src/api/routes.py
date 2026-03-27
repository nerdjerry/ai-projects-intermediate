"""API routes for dataset generation and management.

This module defines the HTTP endpoints exposed by the Synthetic Data Factory.
Each endpoint orchestrates the pipeline — generate → validate → store — by
composing the service objects that implement the core business logic.

Design principles:
  - SRP (Single Responsibility Principle): Route handlers deal only with
    HTTP concerns (parsing requests, returning responses, raising HTTP
    errors).  Heavy lifting is delegated to service classes.
  - DIP (Dependency Inversion Principle): Services are composed here via
    their concrete constructors for simplicity, but every service already
    implements an abstract interface.  In a larger project you would inject
    them via a dependency-injection container so the routes depend only on
    abstractions.
  - OCP (Open/Closed Principle): Adding a new endpoint is additive — you
    define a new handler function without modifying existing ones.

Pydantic models serve as the request / response schemas.  FastAPI uses
them both for automatic validation of incoming JSON and for generating
the OpenAPI documentation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.data_generator import DataGenerator
from ..services.dataset_store import DatasetStore
from ..services.openai_client import OpenAIClient
from ..services.validator import DataValidator

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
# Pydantic ``BaseModel`` subclasses act as data-transfer objects (DTOs).
# FastAPI deserialises incoming JSON into these models and validates fields
# automatically, keeping validation logic out of the route handlers (SRP).
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    """Schema for the POST /generate request body."""

    domain: str = Field(..., description="Knowledge domain (e.g. science, history)")
    num_samples: int = Field(
        default=5, ge=1, le=100, description="Number of Q&A pairs"
    )


class GenerateResponse(BaseModel):
    """Schema returned after a successful generation run."""

    domain: str
    generated: int  # total records produced by the LLM
    validated: int  # records remaining after validation + dedup
    file_path: str  # where the cleaned dataset was saved


class DatasetInfo(BaseModel):
    """Lightweight summary of a stored dataset."""

    domain: str
    record_count: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=GenerateResponse)
async def generate_dataset(req: GenerateRequest) -> GenerateResponse:
    """Generate a synthetic Q&A dataset for the given domain.

    Pipeline: LLM generation → validation → deduplication → storage.
    Each step is handled by a dedicated service (SRP), composed here.
    """
    # Compose the pipeline from independent, single-responsibility services.
    # In production you might inject these via FastAPI's Depends() mechanism
    # to make the route handler easier to unit-test (DIP).
    llm = OpenAIClient()
    generator = DataGenerator(llm_client=llm)
    validator = DataValidator()
    store = DatasetStore()

    # Step 1 — Generate raw Q&A records via the LLM.
    records = await generator.generate_dataset(req.domain, req.num_samples)
    # Step 2 — Filter out low-quality records and remove duplicates.
    validated = validator.validate(records)
    validated = validator.deduplicate(validated)
    # Step 3 — Persist the cleaned dataset to disk.
    file_path = store.save(validated, req.domain)

    return GenerateResponse(
        domain=req.domain,
        generated=len(records),
        validated=len(validated),
        file_path=file_path,
    )


@router.get("/datasets", response_model=list[DatasetInfo])
async def list_datasets() -> list[DatasetInfo]:
    """List all stored datasets with their record counts."""
    store = DatasetStore()
    results: list[DatasetInfo] = []
    for domain in store.list_domains():
        records = store.load(domain)
        results.append(DatasetInfo(domain=domain, record_count=len(records)))
    return results


@router.get("/datasets/{domain}")
async def get_dataset(domain: str) -> list[dict[str, str]]:
    """Retrieve all Q&A records for a specific domain.

    Returns a 404 error if no dataset exists for the requested domain,
    following standard REST conventions for missing resources.
    """
    store = DatasetStore()
    records = store.load(domain)
    if not records:
        raise HTTPException(status_code=404, detail=f"No dataset found for '{domain}'")
    return records
