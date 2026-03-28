"""
OpenAI implementation of the LLM client.

This module provides ``OpenAIClient``, a concrete implementation of
the ``LLMClient`` abstract base class that delegates to the OpenAI
Chat Completions API.

**SOLID – Liskov Substitution Principle (LSP):**
    "Subtypes must be substitutable for their base types."

``OpenAIClient`` is a drop-in replacement wherever ``LLMClient`` is
expected. Any code that depends on ``LLMClient`` — such as
``SummarizationService``, ``QAService``, and ``RiskAnalysisService`` —
works identically whether it receives an ``OpenAIClient``, a future
``AnthropicClient``, or a mock for testing.

**SOLID – Dependency Inversion Principle (DIP):**
This is the *low-level module* that high-level services never import
directly. Instead, an ``OpenAIClient`` instance is created at the
composition root (e.g., in ``app.py`` or a dependency-injection
container) and injected into the services that need it.
"""
from typing import Any

from openai import AsyncOpenAI

from ..interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """Concrete LLM client using the OpenAI API.

    **LSP guarantee:** This class faithfully implements the ``complete``
    contract defined by ``LLMClient``. It accepts a prompt string,
    returns a string, and supports the same ``**kwargs`` pattern.

    **Why AsyncOpenAI?**  LLM API calls are network-bound. Using the
    async client lets FastAPI serve other requests while waiting for
    the OpenAI response, dramatically improving throughput.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """Initialise the OpenAI client.

        Args:
            api_key: OpenAI API key. If ``None``, the SDK falls back
                     to the ``OPENAI_API_KEY`` environment variable.
            model: Default model to use for completions (can be
                   overridden per-call via ``kwargs``).
        """
        # The AsyncOpenAI client handles connection pooling and retries.
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send a prompt to OpenAI and return the response text.

        Args:
            prompt: The user-facing prompt text.
            **kwargs: Optional overrides:
                - ``model``       — use a different model for this call.
                - ``temperature`` — control randomness (default 0.0 for
                                    deterministic legal outputs).

        Returns:
            The assistant's response content as a plain string.
        """
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[{"role": "user", "content": prompt}],
            # temperature=0.0 produces deterministic outputs, which is
            # desirable in the legal domain where consistency matters.
            temperature=kwargs.get("temperature", 0.0),
        )
        # Extract the text content; fall back to empty string if None.
        return response.choices[0].message.content or ""
