"""FastAPI application entry point for the Synthetic Data Factory.

This module creates the top-level ``FastAPI`` application instance and
wires up the versioned API router.  It is intentionally thin — route
definitions and business logic live in separate modules so that this
file only handles application-level configuration.

Design principles:
  - SRP (Single Responsibility Principle): This module is responsible
    *only* for assembling the application object.  Route handlers,
    request schemas, and business logic each live in their own modules.
  - OCP (Open/Closed Principle): New API versions or feature routers can
    be added via ``app.include_router(...)`` without modifying existing
    route code.
"""
from fastapi import FastAPI

from .routes import router

# Create the FastAPI application with metadata used by the auto-generated
# OpenAPI / Swagger docs (available at /docs when the server is running).
app = FastAPI(
    title="Synthetic Data Factory",
    description="Automated Q&A dataset generation pipeline",
    version="0.1.0",
)

# Mount all dataset-related routes under /api/v1.  The prefix keeps the
# URL namespace organised and makes it straightforward to introduce a v2
# router later without breaking existing clients (OCP).
app.include_router(router, prefix="/api/v1")
