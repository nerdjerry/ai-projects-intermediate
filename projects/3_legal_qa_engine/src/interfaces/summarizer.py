"""Summarizer interface (ISP — separate from Q&A)."""
from abc import ABC, abstractmethod


class ISummarizer(ABC):
    """Interface for document summarization."""

    @abstractmethod
    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Summarize a legal document or clause."""
        ...
