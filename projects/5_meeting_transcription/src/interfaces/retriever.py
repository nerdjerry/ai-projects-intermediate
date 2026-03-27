"""
Abstract interface for document retrieval.

This is a *narrower* read-only abstraction compared to ``IIndexer``,
following the Interface Segregation Principle (ISP).  Components that
only need to *search* existing documents depend on ``IRetriever`` instead
of the full ``IIndexer``, reducing unnecessary coupling.

Design Principles:
    - Interface Segregation Principle (ISP): Clients that never index new
      documents should depend on this minimal interface, not on ``IIndexer``.
    - Dependency Inversion Principle (DIP): Upper layers (e.g., a query
      engine) depend on this abstraction rather than a concrete storage
      implementation.
"""

from abc import ABC, abstractmethod
from typing import Any


class IRetriever(ABC):
    """Read-only contract for retrieving relevant documents.

    This interface is intentionally minimal — a single ``retrieve``
    method — so that query engines and other consumers stay decoupled
    from the indexing lifecycle.
    """

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Find documents relevant to the given query.

        Args:
            query: A natural-language search string.
            top_k: Maximum number of documents to return.

        Returns:
            A ranked list of document dictionaries ordered by relevance.
        """
        ...
