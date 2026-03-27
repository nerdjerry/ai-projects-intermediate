"""Tests for the SessionMemory."""
from src.services.memory_manager import SessionMemory


class TestSessionMemory:
    def setup_method(self):
        self.memory = SessionMemory()

    def test_store_and_recall(self):
        self.memory.store("key1", "value1")
        assert self.memory.recall("key1") == "value1"

    def test_recall_missing(self):
        assert self.memory.recall("nonexistent") is None

    def test_search(self):
        self.memory.store("grocery_spending", 150.0)
        self.memory.store("rent_payment", 1200.0)
        results = self.memory.search("grocery")
        assert len(results) == 1
        assert results[0]["key"] == "grocery_spending"

    def test_search_limit(self):
        for i in range(10):
            self.memory.store(f"item_{i}", f"value_{i}")
        results = self.memory.search("item", limit=3)
        assert len(results) == 3

    def test_clear(self):
        self.memory.store("key", "value")
        self.memory.clear()
        assert self.memory.recall("key") is None
        assert self.memory.size == 0

    def test_size(self):
        assert self.memory.size == 0
        self.memory.store("a", 1)
        self.memory.store("b", 2)
        assert self.memory.size == 2
