"""
Tests for ``SessionMemory`` — the in-memory implementation of the
read/write memory interfaces.

These tests exercise both ``IMemoryReader`` and ``IMemoryWriter`` methods,
confirming that ``SessionMemory`` correctly fulfils both contracts (LSP).

Testing Strategy:
    - **Store & recall**: Round-trip persistence of a single entry.
    - **Recall missing**: Verifies ``None`` return for absent keys.
    - **Search**: Validates substring matching across keys/values.
    - **Search limit**: Ensures the ``limit`` parameter is respected.
    - **Clear**: Confirms full reset of state.
    - **Size**: Checks the convenience property after mutations.
"""

from src.services.memory_manager import SessionMemory


class TestSessionMemory:
    """Unit tests for the SessionMemory key-value store."""

    def setup_method(self):
        """Create a fresh memory instance for each test (test isolation)."""
        self.memory = SessionMemory()

    def test_store_and_recall(self):
        """Storing a value should make it retrievable via recall."""
        self.memory.store("key1", "value1")
        assert self.memory.recall("key1") == "value1"

    def test_recall_missing(self):
        """Recalling a key that was never stored should return None."""
        assert self.memory.recall("nonexistent") is None

    def test_search(self):
        """Search should return entries whose keys match the query."""
        self.memory.store("grocery_spending", 150.0)
        self.memory.store("rent_payment", 1200.0)
        results = self.memory.search("grocery")
        assert len(results) == 1
        assert results[0]["key"] == "grocery_spending"

    def test_search_limit(self):
        """Search should respect the limit parameter."""
        for i in range(10):
            self.memory.store(f"item_{i}", f"value_{i}")
        results = self.memory.search("item", limit=3)
        assert len(results) == 3

    def test_clear(self):
        """After clear(), the store should be completely empty."""
        self.memory.store("key", "value")
        self.memory.clear()
        assert self.memory.recall("key") is None
        assert self.memory.size == 0

    def test_size(self):
        """Size should reflect the number of stored entries."""
        assert self.memory.size == 0
        self.memory.store("a", 1)
        self.memory.store("b", 2)
        assert self.memory.size == 2
