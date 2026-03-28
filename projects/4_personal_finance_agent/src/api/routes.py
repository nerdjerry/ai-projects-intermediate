"""API routes for the Personal Finance Agent.

This module defines the FastAPI endpoints for managing transactions, chatting
with the finance agent, and searching conversation memory.

Design principles:
  - DIP: All services are injected via FastAPI's dependency injection, making
    them easily swappable for testing or alternative implementations.
  - SRP: Routes only handle HTTP concerns; business logic lives in services.
  - ISP: Memory is split into IMemoryReader/IMemoryWriter interfaces.

Note on dependency injection:
  FastAPI's `Depends()` system creates service instances per-request by default.
  We use `app.state` (set during lifespan) to share instances across requests,
  which gives us explicit lifecycle control. For production, these would be
  backed by a real database; the in-memory versions are for demos and testing.
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from ..services.insight_generator import SimpleInsightGenerator
from ..services.memory_manager import SessionMemory
from ..services.transaction_service import MockTransactionService

router = APIRouter()


# --- Schemas ---
# Pydantic models define the API contract and provide automatic validation.


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    amount: float = Field(..., description="Transaction amount in dollars")
    category: str = Field(default="uncategorized", description="Spending category")
    description: str = Field(default="", description="Transaction description")


class TransactionResponse(BaseModel):
    """Schema for a transaction returned by the API."""
    id: str
    amount: float
    category: str
    description: str
    date: str


class SummaryResponse(BaseModel):
    """Spending summary for a time period."""
    period: str
    total_spending: float
    transaction_count: int
    by_category: dict[str, float]


class ChatRequest(BaseModel):
    """Chat message from the user."""
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """Agent reply with generated insights."""
    reply: str
    insights: list[str] = Field(default_factory=list)


# --- Dependency injection helpers ---
# These functions retrieve service instances from FastAPI's app.state,
# which is initialized during the application lifespan. This approach
# gives us explicit control over object lifecycle and makes testing easier
# (override dependencies in tests to inject mocks).

def get_tx_service(request: Request) -> MockTransactionService:
    """Retrieve the transaction service from app state (DIP)."""
    return request.app.state.tx_service


def get_memory(request: Request) -> SessionMemory:
    """Retrieve the session memory from app state (DIP)."""
    return request.app.state.memory


def get_insight_gen(request: Request) -> SimpleInsightGenerator:
    """Retrieve the insight generator from app state (DIP)."""
    return request.app.state.insight_gen


# --- Endpoints ---


@router.post("/transactions", response_model=TransactionResponse)
async def add_transaction(
    req: TransactionCreate,
    tx_service: MockTransactionService = Depends(get_tx_service),
    memory: SessionMemory = Depends(get_memory),
) -> Any:
    """Add a new transaction and store it in session memory.

    The transaction is persisted in the transaction service and also
    cached in session memory for quick recall during chat interactions.
    """
    record = tx_service.add_transaction(req.model_dump())
    # Store in memory so the chat agent can recall recent transactions
    memory.store(f"tx_{record['id']}", record)
    return record


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    limit: int = 50,
    offset: int = 0,
    tx_service: MockTransactionService = Depends(get_tx_service),
) -> Any:
    """List transactions with pagination.

    Args:
        limit: Maximum number of transactions to return (default: 50).
        offset: Number of transactions to skip (for pagination).
    """
    return tx_service.get_transactions(limit=limit, offset=offset)


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    period: str = "month",
    tx_service: MockTransactionService = Depends(get_tx_service),
) -> Any:
    """Get spending summary for a time period."""
    return tx_service.get_summary(period)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    tx_service: MockTransactionService = Depends(get_tx_service),
    memory: SessionMemory = Depends(get_memory),
    insight_gen: SimpleInsightGenerator = Depends(get_insight_gen),
) -> ChatResponse:
    """Chat with the finance agent.

    Fetches ALL transactions (not just the first page) to ensure the
    agent's insights reflect the complete financial picture. The analysis
    and conversation are stored in memory for future reference.
    """
    # Fetch all transactions for complete analysis (no silent truncation)
    transactions = tx_service.get_transactions(limit=0)
    insights = await insight_gen.generate_insights(transactions)

    # Store conversation in memory for recall in future interactions
    memory.store(f"chat_{memory.size}", {"message": req.message, "insights": insights})

    reply = f"Based on {len(transactions)} transactions: " + "; ".join(insights)
    return ChatResponse(reply=reply, insights=insights)


@router.get("/memory/search")
async def search_memory(
    query: str,
    limit: int = 5,
    memory: SessionMemory = Depends(get_memory),
) -> list[dict[str, Any]]:
    """Search through agent memory by keyword.

    Useful for recalling past conversations or finding specific transactions
    that were discussed in earlier chat sessions.
    """
    return memory.search(query, limit=limit)
