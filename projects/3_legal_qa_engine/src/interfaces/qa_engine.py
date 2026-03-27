"""Q&A engine interface (ISP — separate from summarization)."""
from abc import ABC, abstractmethod
from typing import Any


class IQAEngine(ABC):
    """Interface for legal question-answering."""

    @abstractmethod
    async def ask(self, question: str, context: str, **kwargs: Any) -> str:
        """Answer a question given legal context."""
        ...
