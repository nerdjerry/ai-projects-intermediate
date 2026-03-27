"""Tests for the InMemoryIndexer."""
import pytest
from src.services.in_memory_indexer import InMemoryIndexer


class TestInMemoryIndexer:
    def setup_method(self):
        self.indexer = InMemoryIndexer()

    @pytest.mark.asyncio
    async def test_index_documents(self):
        docs = [
            {"text": "Discussed the project roadmap", "speaker": "Alice"},
            {"text": "Budget review completed", "speaker": "Bob"},
        ]
        count = await self.indexer.index(docs)
        assert count == 2
        assert self.indexer.document_count == 2

    @pytest.mark.asyncio
    async def test_search(self):
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
        docs = [{"text": "Hello world", "speaker": "Alice"}]
        await self.indexer.index(docs)
        results = await self.indexer.search("xyz_nonexistent")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_top_k(self):
        docs = [{"text": f"Document about topic {i}", "speaker": "A"} for i in range(10)]
        await self.indexer.index(docs)
        results = await self.indexer.search("topic", top_k=3)
        assert len(results) <= 3
