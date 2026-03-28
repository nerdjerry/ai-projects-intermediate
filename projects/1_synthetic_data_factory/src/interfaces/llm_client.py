"""Abstract LLM client interface for dependency inversion.

This module defines the contract that every LLM provider must satisfy.
By programming against this abstraction rather than a concrete SDK, the rest
of the codebase is shielded from vendor-specific details.

Design principles:
  - DIP (Dependency Inversion Principle): High-level modules (DataGenerator,
    API routes) depend on this abstraction, not on OpenAI or any other
    concrete client.  Swapping providers only requires a new implementation
    of this interface — zero changes to consumers.
  - ISP (Interface Segregation Principle): The interface exposes only the
    two methods that callers actually need (single and batch generation),
    keeping it small and focused.
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract base class that all LLM provider clients must implement.

    Any concrete subclass (e.g. ``OpenAIClient``, a future ``AnthropicClient``)
    must implement ``generate`` and ``generate_batch``.  Because Python's
    ``ABC`` enforces this at instantiation time, callers are guaranteed a
    consistent API regardless of the underlying provider.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text from a single prompt.

        Args:
            prompt: The user-facing prompt string sent to the LLM.
            **kwargs: Provider-specific overrides (model name, temperature, …).

        Returns:
            The generated text as a plain string.
        """
        ...

    @abstractmethod
    async def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate text from multiple prompts (potentially concurrently).

        Concrete implementations may parallelise the calls for throughput.

        Args:
            prompts: A list of prompt strings.
            **kwargs: Provider-specific overrides forwarded to each call.

        Returns:
            A list of generated text strings, one per input prompt.
        """
        ...
