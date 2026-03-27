"""Abstract LLM client for legal domain."""
from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract LLM provider (Dependency Inversion)."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        ...
