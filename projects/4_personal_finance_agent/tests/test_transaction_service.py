"""
Tests for ``MockTransactionService`` — the in-memory transaction store.

These tests verify the ``ITransactionService`` contract (LSP) by exercising
CRUD operations and summary computation.

Testing Strategy:
    - **Add**: Confirms that a new transaction gets an ``id`` and retains
      its fields.
    - **Get (list)**: Verifies retrieval of all stored transactions.
    - **Pagination**: Ensures ``limit`` and ``offset`` correctly window
      the result set.
    - **Summary**: Validates aggregate computation (total, count, and
      per-category breakdown).
    - **Summary (empty)**: Checks the edge case of zero transactions.
"""

from src.services.transaction_service import MockTransactionService


class TestMockTransactionService:
    """Unit tests for the mock in-memory transaction service."""

    def setup_method(self):
        """Create a fresh service instance for each test (test isolation)."""
        self.service = MockTransactionService()

    def test_add_transaction(self):
        """Adding a transaction should return it with a generated 'id'."""
        result = self.service.add_transaction({"amount": 50.0, "category": "food"})
        assert "id" in result
        assert result["amount"] == 50.0
        assert result["category"] == "food"

    def test_get_transactions(self):
        """All added transactions should be returned by get_transactions."""
        self.service.add_transaction({"amount": 10.0})
        self.service.add_transaction({"amount": 20.0})
        txns = self.service.get_transactions()
        assert len(txns) == 2

    def test_get_transactions_pagination(self):
        """Pagination via limit and offset should window the result set."""
        for i in range(5):
            self.service.add_transaction({"amount": float(i)})
        # Skip the first transaction, take two
        page = self.service.get_transactions(limit=2, offset=1)
        assert len(page) == 2

    def test_get_summary(self):
        """Summary should aggregate total, count, and per-category spend."""
        self.service.add_transaction({"amount": 100.0, "category": "food"})
        self.service.add_transaction({"amount": 50.0, "category": "transport"})
        summary = self.service.get_summary()
        assert summary["total_spending"] == 150.0
        assert summary["transaction_count"] == 2
        assert summary["by_category"]["food"] == 100.0

    def test_get_summary_empty(self):
        """Summary with no transactions should return zeros."""
        summary = self.service.get_summary()
        assert summary["total_spending"] == 0
        assert summary["transaction_count"] == 0
