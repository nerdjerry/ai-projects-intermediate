"""Abstract retriever — decouple retrieval strategy (DIP)."""
from abc import ABC, abstractmethod
from typing import Any


class IRetriever(ABC):
    """Abstract document retriever."""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        ...
