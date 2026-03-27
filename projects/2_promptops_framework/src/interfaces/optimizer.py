"""Optimizer interface — separate from testing (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class IOptimizer(ABC):
    """Interface for prompt optimization."""

    @abstractmethod
    async def optimize(
        self, prompt_template: str, examples: list[dict[str, str]], **kwargs: Any
    ) -> str:
        """Return an improved prompt template."""
        ...
