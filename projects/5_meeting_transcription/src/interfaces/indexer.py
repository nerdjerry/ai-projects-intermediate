"""Indexer interface for embedding storage."""
from abc import ABC, abstractmethod
from typing import Any


class IIndexer(ABC):
    """Abstract document indexer (DIP)."""

    @abstractmethod
    async def index(self, documents: list[dict[str, Any]]) -> int:
        """Index documents and return count of indexed items."""
        ...

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search indexed documents by semantic similarity."""
        ...
