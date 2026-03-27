"""Query engine interface — separate from transcription (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class IQueryEngine(ABC):
    """Abstract query engine for RAG over transcripts (ISP)."""

    @abstractmethod
    async def query(self, question: str, **kwargs: Any) -> str:
        """Answer a question using indexed transcripts."""
        ...
