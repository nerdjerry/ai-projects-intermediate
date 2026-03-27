"""
Abstract interface for document indexing and search.

An indexer is responsible for storing documents (typically transcription
segments) in a way that supports efficient retrieval later.  This forms
the **"Index"** step in a Retrieval-Augmented Generation (RAG) pipeline.

Design Principles:
    - Dependency Inversion Principle (DIP): Consumers depend on this
      abstraction so the storage backend can be swapped (in-memory, FAISS,
      Pinecone, etc.) without code changes.
    - Single Responsibility Principle (SRP): Indexing and querying are
      combined in one interface because they are tightly coupled; however,
      read-only retrieval is further separated into ``IRetriever`` (ISP).
    - Interface Segregation Principle (ISP): ``IRetriever`` exists as a
      narrower read-only view for components that do not need to index
      new documents.
"""

from abc import ABC, abstractmethod
from typing import Any


class IIndexer(ABC):
    """Contract for services that index and search documents.

    Implementations range from a simple in-memory keyword matcher (used
    for tests) to vector-database-backed stores for production RAG.
    """

    @abstractmethod
    async def index(self, documents: list[dict[str, Any]]) -> int:
        """Ingest a batch of documents into the index.

        Args:
            documents: A list of dictionaries, each containing at least a
                ``text`` key and optional metadata (``speaker``, timestamps).

        Returns:
            The number of documents successfully indexed.
        """
        ...

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve documents most relevant to the query.

        In a production system this would use semantic (embedding-based)
        similarity; simpler implementations may fall back to keyword
        matching.

        Args:
            query: The search string or question.
            top_k: Maximum number of results to return.

        Returns:
            A ranked list of document dictionaries.
        """
        ...
