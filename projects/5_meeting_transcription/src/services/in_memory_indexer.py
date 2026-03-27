"""In-memory indexer for development (LSP — swap for pgvector)."""
from typing import Any

from ..interfaces.indexer import IIndexer


class InMemoryIndexer(IIndexer):
    """Simple in-memory document index using keyword matching."""

    def __init__(self) -> None:
        self._documents: list[dict[str, Any]] = []

    async def index(self, documents: list[dict[str, Any]]) -> int:
        self._documents.extend(documents)
        return len(documents)

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_lower = query.lower()
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in self._documents:
            text = doc.get("text", "").lower()
            # Simple keyword relevance score
            words = query_lower.split()
            score = sum(1.0 for w in words if w in text)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    @property
    def document_count(self) -> int:
        return len(self._documents)
