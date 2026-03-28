"""
FastAPI application factory for the PromptOps Framework.

This module serves as the **composition root** for the REST API layer.  It
creates the ``FastAPI`` application instance and wires together the router(s)
defined in ``routes.py``.

Architecture notes
------------------
* The application object is intentionally *thin* — it contains no business
  logic.  All endpoint handlers live in ``routes.py``, and all domain logic
  lives in the ``services`` package.  This separation follows the **Single
  Responsibility Principle (SRP)**: the app module's only job is bootstrapping.
* Routes are mounted under the ``/api/v1`` prefix so the API can be versioned
  cleanly if a ``v2`` is introduced later.
* ``app`` is exposed as a module-level variable so ASGI servers (``uvicorn``,
  ``gunicorn``) can discover it with a simple import path like
  ``src.api.app:app``.
"""

from fastapi import FastAPI

from .routes import router

# ---------------------------------------------------------------------------
# Application instance — the single entry point for the ASGI server.
# ---------------------------------------------------------------------------
app = FastAPI(
    title="PromptOps Framework",
    description="CI/CD for prompts — evaluate, version, optimize",
    version="0.1.0",
)

# Mount the v1 API router.  Using a prefix keeps the URL structure organized
# and makes future API versioning straightforward.
app.include_router(router, prefix="/api/v1")
