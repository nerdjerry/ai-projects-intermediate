"""
FastAPI application for the Legal Q&A Engine.

This module is the **composition root** of the web application — the
single place where the FastAPI ``app`` instance is created and all
routers are mounted.

**SOLID – Single Responsibility Principle (SRP):**
This module does only one thing: bootstrap the application. Route
handlers, business logic, and data processing live in their own
modules. This separation keeps the entry point clean and makes it
easy to locate configuration concerns.

**Design decision:** The API is versioned via a ``/api/v1`` prefix.
This allows future breaking changes to be introduced under ``/api/v2``
without disrupting existing consumers — a common REST API best practice.
"""
from fastapi import FastAPI

from .routes import router

# Create the FastAPI application instance with OpenAPI metadata.
# ``title``, ``description``, and ``version`` populate the auto-generated
# Swagger/OpenAPI documentation at ``/docs``.
app = FastAPI(
    title="Legal Q&A Engine",
    description="Domain-specialized legal LLM — summarize, analyze risk, ask questions",
    version="0.1.0",
)

# Mount all API routes under the ``/api/v1`` prefix.
# Using ``include_router`` keeps route definitions separate from app
# setup, following the SRP and making the codebase modular.
app.include_router(router, prefix="/api/v1")
