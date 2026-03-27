"""API routes for dataset generation and management."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.data_generator import DataGenerator
from ..services.dataset_store import DatasetStore
from ..services.openai_client import OpenAIClient
from ..services.validator import DataValidator

router = APIRouter()

# --- Request / Response schemas ------------------------------------------------


class GenerateRequest(BaseModel):
    domain: str = Field(..., description="Knowledge domain (e.g. science, history)")
    num_samples: int = Field(
        default=5, ge=1, le=100, description="Number of Q&A pairs"
    )


class GenerateResponse(BaseModel):
    domain: str
    generated: int
    validated: int
    file_path: str


class DatasetInfo(BaseModel):
    domain: str
    record_count: int


# --- Endpoints ------------------------------------------------------------------


@router.post("/generate", response_model=GenerateResponse)
async def generate_dataset(req: GenerateRequest) -> GenerateResponse:
    """Generate a synthetic Q&A dataset for the given domain."""
    llm = OpenAIClient()
    generator = DataGenerator(llm_client=llm)
    validator = DataValidator()
    store = DatasetStore()

    records = await generator.generate_dataset(req.domain, req.num_samples)
    validated = validator.validate(records)
    validated = validator.deduplicate(validated)
    file_path = store.save(validated, req.domain)

    return GenerateResponse(
        domain=req.domain,
        generated=len(records),
        validated=len(validated),
        file_path=file_path,
    )


@router.get("/datasets", response_model=list[DatasetInfo])
async def list_datasets() -> list[DatasetInfo]:
    """List all stored datasets."""
    store = DatasetStore()
    results: list[DatasetInfo] = []
    for domain in store.list_domains():
        records = store.load(domain)
        results.append(DatasetInfo(domain=domain, record_count=len(records)))
    return results


@router.get("/datasets/{domain}")
async def get_dataset(domain: str) -> list[dict[str, str]]:
    """Retrieve records for a specific domain."""
    store = DatasetStore()
    records = store.load(domain)
    if not records:
        raise HTTPException(status_code=404, detail=f"No dataset found for '{domain}'")
    return records
