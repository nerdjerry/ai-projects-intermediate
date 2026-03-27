"""Tests for the MockTransactionService."""
from src.services.transaction_service import MockTransactionService


class TestMockTransactionService:
    def setup_method(self):
        self.service = MockTransactionService()

    def test_add_transaction(self):
        result = self.service.add_transaction({"amount": 50.0, "category": "food"})
        assert "id" in result
        assert result["amount"] == 50.0
        assert result["category"] == "food"

    def test_get_transactions(self):
        self.service.add_transaction({"amount": 10.0})
        self.service.add_transaction({"amount": 20.0})
        txns = self.service.get_transactions()
        assert len(txns) == 2

    def test_get_transactions_pagination(self):
        for i in range(5):
            self.service.add_transaction({"amount": float(i)})
        page = self.service.get_transactions(limit=2, offset=1)
        assert len(page) == 2

    def test_get_summary(self):
        self.service.add_transaction({"amount": 100.0, "category": "food"})
        self.service.add_transaction({"amount": 50.0, "category": "transport"})
        summary = self.service.get_summary()
        assert summary["total_spending"] == 150.0
        assert summary["transaction_count"] == 2
        assert summary["by_category"]["food"] == 100.0

    def test_get_summary_empty(self):
        summary = self.service.get_summary()
        assert summary["total_spending"] == 0
        assert summary["transaction_count"] == 0
