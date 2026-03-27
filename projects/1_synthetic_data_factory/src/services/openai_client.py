"""OpenAI implementation of the LLM client.

This module provides the concrete ``OpenAIClient`` that wraps the OpenAI
``AsyncOpenAI`` SDK.  It fulfils the ``LLMClient`` abstract interface, so
it can be injected anywhere the system needs an LLM — without tying the
rest of the code to OpenAI-specific types.

Design principles:
  - LSP (Liskov Substitution Principle): ``OpenAIClient`` can replace the
    abstract ``LLMClient`` in any context.  It honours the base-class
    contracts (same parameter semantics, same return types) so callers
    never need to know which concrete client they're using.
  - DIP (Dependency Inversion Principle): This module is the *only* place
    that imports the ``openai`` SDK.  Every other module depends on the
    abstract ``LLMClient`` interface, keeping vendor lock-in to a minimum.
  - SRP (Single Responsibility Principle): The class is responsible only
    for translating abstract generate/generate_batch calls into OpenAI API
    requests — parsing and validation happen elsewhere.
"""
import asyncio
from typing import Any

from openai import AsyncOpenAI

from ..interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """Concrete LLM client that delegates to the OpenAI Chat Completions API.

    This class is Liskov-substitutable for ``LLMClient``: every method
    signature matches the abstract base, and the behavioural post-conditions
    (returning plain strings) are preserved.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """Initialise the OpenAI async client.

        Args:
            api_key: Optional API key.  When ``None`` the SDK falls back to
                the ``OPENAI_API_KEY`` environment variable.
            model: Default chat model used for completions.
        """
        # Encapsulate the third-party SDK behind private attributes so that
        # the rest of the codebase never touches it directly.
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI chat completions.

        Callers can override the model or temperature via **kwargs without
        changing the method signature — this keeps the interface stable
        while allowing per-call flexibility.
        """
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
        )
        # OpenAI may return None for content in edge cases; default to "".
        return response.choices[0].message.content or ""

    async def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate text for multiple prompts concurrently.

        Uses ``asyncio.gather`` to fire all requests in parallel, which is
        significantly faster than sequential awaits when the bottleneck is
        network I/O rather than CPU.
        """
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
