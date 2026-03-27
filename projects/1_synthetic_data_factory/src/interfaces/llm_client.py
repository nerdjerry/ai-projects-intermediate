"""Abstract LLM client interface for dependency inversion."""
from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract base class for LLM providers (Dependency Inversion)."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text from a prompt."""
        ...

    @abstractmethod
    async def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate text from multiple prompts."""
        ...
