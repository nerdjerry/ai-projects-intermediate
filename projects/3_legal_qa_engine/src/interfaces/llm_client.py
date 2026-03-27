"""
Abstract LLM client for the legal domain.

This module defines the abstract base class (ABC) that all LLM provider
implementations must inherit from. It is the cornerstone of the
**Dependency Inversion Principle (DIP)** in this project:

    "High-level modules should not depend on low-level modules.
     Both should depend on abstractions."

By programming against this abstraction rather than a concrete SDK
(e.g., OpenAI, Anthropic), the rest of the application — services,
API routes, and the UI — remain completely decoupled from any specific
LLM vendor. Swapping providers requires only a new subclass, not
changes across the codebase.

Design pattern: **Strategy Pattern** — the concrete LLM client is
injected at runtime, allowing the calling code to remain unchanged.
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract LLM provider — the central abstraction for all LLM calls.

    **SOLID – Dependency Inversion Principle (DIP):**
    Every service that needs LLM completions depends on *this* abstract
    class, not on a concrete implementation like ``OpenAIClient``.
    This makes the system easy to test (inject a mock) and easy to
    extend (add ``AnthropicClient``, ``LocalLlamaClient``, etc.).

    **SOLID – Open/Closed Principle (OCP):**
    New LLM providers can be added by creating a new subclass without
    modifying any existing code.
    """

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The text prompt to send to the language model.
            **kwargs: Provider-specific options (e.g., temperature, model).

        Returns:
            The model's text response as a string.

        Note:
            This method is ``async`` because LLM API calls are I/O-bound;
            using ``await`` lets the event loop handle other requests
            concurrently while waiting for the provider's response.
        """
        ...
