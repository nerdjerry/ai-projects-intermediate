"""API routes for the Personal Finance Agent."""
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.insight_generator import SimpleInsightGenerator
from ..services.memory_manager import SessionMemory
from ..services.transaction_service import MockTransactionService

router = APIRouter()

# --- Shared state (for demo; production would use DI) ---
tx_service = MockTransactionService()
memory = SessionMemory()
insight_gen = SimpleInsightGenerator()

# --- Schemas ---

class TransactionCreate(BaseModel):
    amount: float = Field(..., description="Transaction amount")
    category: str = Field(default="uncategorized")
    description: str = Field(default="")


class TransactionResponse(BaseModel):
    id: str
    amount: float
    category: str
    description: str
    date: str


class SummaryResponse(BaseModel):
    period: str
    total_spending: float
    transaction_count: int
    by_category: dict[str, float]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str
    insights: list[str] = Field(default_factory=list)


# --- Endpoints ---

@router.post("/transactions", response_model=TransactionResponse)
async def add_transaction(req: TransactionCreate) -> Any:
    """Add a new transaction."""
    record = tx_service.add_transaction(req.model_dump())
    memory.store(f"tx_{record['id']}", record)
    return record


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(limit: int = 50, offset: int = 0) -> Any:
    """List transactions."""
    return tx_service.get_transactions(limit=limit, offset=offset)


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(period: str = "month") -> Any:
    """Get spending summary."""
    return tx_service.get_summary(period)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Chat with the finance agent."""
    transactions = tx_service.get_transactions()
    insights = await insight_gen.generate_insights(transactions)

    # Store conversation in memory
    memory.store(f"chat_{memory.size}", {"message": req.message, "insights": insights})

    reply = f"Based on {len(transactions)} transactions: " + "; ".join(insights)
    return ChatResponse(reply=reply, insights=insights)


@router.get("/memory/search")
async def search_memory(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search through agent memory."""
    return memory.search(query, limit=limit)
