"""FastAPI application for the Personal Finance Agent.

Sets up the application with proper lifecycle management for services.
Services are initialized during app startup (lifespan) and stored in
app.state, making them available to all routes via dependency injection.

This approach avoids module-level singletons, gives explicit control over
service lifecycle, and makes the app easier to test.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from ..services.insight_generator import SimpleInsightGenerator
from ..services.memory_manager import SessionMemory
from ..services.transaction_service import MockTransactionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared services on startup, clean up on shutdown.

    Using a lifespan context manager is the recommended FastAPI pattern
    for managing service instances that need to live across requests.
    This replaces module-level singletons, giving us:
      - Explicit initialization and cleanup
      - Easy swapping for tests (override app.state)
      - No unbounded memory growth from leaked references
    """
    # Initialize services — swap these for real DB-backed implementations
    # in production by changing which classes are instantiated here.
    app.state.tx_service = MockTransactionService()
    app.state.memory = SessionMemory()
    app.state.insight_gen = SimpleInsightGenerator()
    yield
    # Cleanup: clear memory on shutdown to release resources
    app.state.memory.clear()


app = FastAPI(
    title="Personal Finance Agent",
    description="Stateful AI agent with memory for personal finance",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")
