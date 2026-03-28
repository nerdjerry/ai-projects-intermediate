"""
Tests for ``InMemoryIndexer`` — the keyword-based document indexer.

These tests verify that documents can be indexed and subsequently
retrieved via keyword search, confirming that ``InMemoryIndexer``
honours the ``IIndexer`` contract (LSP).

Testing Strategy:
    - **Index**: Stores documents and verifies the returned count.
    - **Search (hit)**: Ensures keyword matches rank relevant documents.
    - **Search (miss)**: Confirms that unrelated queries return nothing.
    - **Search top_k**: Validates that the result set is capped correctly.
"""

import pytest
from src.services.in_memory_indexer import InMemoryIndexer


class TestInMemoryIndexer:
    """Unit tests for the InMemoryIndexer keyword search store."""

    def setup_method(self):
        """Create a fresh indexer for each test (test isolation)."""
        self.indexer = InMemoryIndexer()

    @pytest.mark.asyncio
    async def test_index_documents(self):
        """Indexing should return the number of documents stored."""
        docs = [
            {"text": "Discussed the project roadmap", "speaker": "Alice"},
            {"text": "Budget review completed", "speaker": "Bob"},
        ]
        count = await self.indexer.index(docs)
        assert count == 2
        assert self.indexer.document_count == 2

    @pytest.mark.asyncio
    async def test_search(self):
        """Searching for a keyword present in a document should return it."""
        docs = [
            {"text": "Project roadmap planning session", "speaker": "Alice"},
            {"text": "Budget allocation for Q2", "speaker": "Bob"},
        ]
        await self.indexer.index(docs)
        results = await self.indexer.search("roadmap")
        assert len(results) >= 1
        assert "roadmap" in results[0]["text"].lower()

    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """A query with no matching keywords should return an empty list."""
        docs = [{"text": "Hello world", "speaker": "Alice"}]
        await self.indexer.index(docs)
        results = await self.indexer.search("xyz_nonexistent")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_top_k(self):
        """Results should be limited to the specified top_k value."""
        docs = [{"text": f"Document about topic {i}", "speaker": "A"} for i in range(10)]
        await self.indexer.index(docs)
        results = await self.indexer.search("topic", top_k=3)
        assert len(results) <= 3
