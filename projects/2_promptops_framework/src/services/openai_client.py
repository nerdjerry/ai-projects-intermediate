"""
OpenAI implementation of the abstract LLM client.

This module provides ``OpenAIClient``, a concrete subclass of the
``LLMClient`` abstraction that delegates to the OpenAI Chat Completions API.

SOLID principles at play
------------------------
* **Liskov Substitution Principle (LSP)** — ``OpenAIClient`` can be used
  anywhere a ``LLMClient`` is expected without altering the correctness of
  the program.  It respects the same async signature and return type.
* **Dependency Inversion Principle (DIP)** — The rest of the application
  never imports ``OpenAIClient`` directly; it receives a ``LLMClient``
  instance via constructor injection.  This module is only referenced at the
  *composition root* (the place where concrete objects are wired together).
* **Single Responsibility Principle (SRP)** — This class does exactly one
  thing: translate the generic ``complete(prompt)`` call into an OpenAI API
  request.  Prompt rendering, evaluation, and storage are handled elsewhere.

Swapping providers
------------------
To use a different LLM provider (Anthropic, Mistral, a local model, …),
create a new ``LLMClient`` subclass — no changes to this file or any
consumer are required.
"""

from typing import Any

from openai import AsyncOpenAI

from ..interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """Concrete ``LLMClient`` backed by the OpenAI Chat Completions API.

    This class is **Liskov-substitutable**: it can replace any ``LLMClient``
    without breaking calling code, because it faithfully implements the
    ``complete`` contract defined by the abstract base class.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """Initialise the client.

        Parameters
        ----------
        api_key : str | None
            OpenAI API key.  When ``None`` the SDK falls back to the
            ``OPENAI_API_KEY`` environment variable.
        model : str
            Default model identifier (can be overridden per-call via kwargs).
        """
        # AsyncOpenAI handles connection pooling, retries, and auth internally.
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send *prompt* to OpenAI and return the assistant's reply.

        Keyword arguments ``model`` and ``temperature`` are forwarded to the
        API; any other kwargs are currently ignored.
        """
        response = await self._client.chat.completions.create(
            # Allow callers to override the model on a per-request basis.
            model=kwargs.get("model", self._model),
            # Wrap the raw prompt as a single "user" message.
            messages=[{"role": "user", "content": prompt}],
            # Default temperature 0.0 for deterministic, reproducible output.
            temperature=kwargs.get("temperature", 0.0),
        )
        # Return the text content; fall back to empty string if None.
        return response.choices[0].message.content or ""
