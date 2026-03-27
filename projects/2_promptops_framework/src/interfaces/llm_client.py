"""Abstract LLM client interface."""
from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract LLM provider (Dependency Inversion Principle)."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Run a prompt and return the completion text."""
        ...
