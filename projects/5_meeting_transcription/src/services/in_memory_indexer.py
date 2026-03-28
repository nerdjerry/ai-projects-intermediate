"""In-memory indexer for development (LSP — swap for pgvector).

This simple indexer stores documents in a list and searches using keyword
matching. It's useful for development and testing without external
dependencies. For production, swap with a pgvector-backed implementation
that provides semantic search via embeddings.

Design principles:
  - LSP: Implements IIndexer, so it can be substituted for any other indexer
    (e.g., PgVectorIndexer) without changing the MeetingService code.
  - SRP: Only handles indexing and searching, not transcription or diarization.
"""
from typing import Any

from ..interfaces.indexer import IIndexer


class InMemoryIndexer(IIndexer):
    """Simple in-memory document index using keyword matching.

    Documents are stored in a list and searched by checking whether query
    words appear in the document text. Relevance is scored by counting
    the number of matching words.

    For production use, replace with a vector-based indexer (e.g., pgvector)
    that computes semantic similarity using embeddings.
    """

    def __init__(self) -> None:
        """Initialize with an empty document list."""
        self._documents: list[dict[str, Any]] = []

    async def index(self, documents: list[dict[str, Any]]) -> int:
        """Add documents to the index and return the count of indexed items."""
        self._documents.extend(documents)
        return len(documents)

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search indexed documents by keyword relevance.

        Each query word is checked against each document's text field.
        Documents are ranked by the number of matching words and the
        top_k most relevant are returned.

        Args:
            query: Search query string (split into words for matching).
            top_k: Maximum number of results to return.

        Returns:
            List of matching documents sorted by relevance (highest first).
        """
        query_lower = query.lower()
        # Pre-compute the query words once outside the loop to avoid
        # redundant string splitting on every document iteration.
        words = query_lower.split()

        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in self._documents:
            text = doc.get("text", "").lower()
            # Score = count of query words found in the document text
            score = sum(1.0 for w in words if w in text)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    async def clear(self) -> None:
        """Clear all indexed documents (useful for testing and lifecycle mgmt)."""
        self._documents.clear()

    @property
    def document_count(self) -> int:
        """Return the number of indexed documents."""
        return len(self._documents)
