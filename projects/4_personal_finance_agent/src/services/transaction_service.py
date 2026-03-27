"""Mock transaction service (SRP — data access only)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from ..interfaces.transaction_service import ITransactionService


class MockTransactionService(ITransactionService):
    """In-memory transaction store (swap for real DB via LSP)."""

    def __init__(self) -> None:
        self._transactions: list[dict[str, Any]] = []

    def add_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "amount": transaction["amount"],
            "category": transaction.get("category", "uncategorized"),
            "description": transaction.get("description", ""),
            "date": transaction.get("date", datetime.now(timezone.utc).isoformat()),
        }
        self._transactions.append(record)
        return record

    def get_transactions(
        self, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._transactions[offset : offset + limit]

    def get_summary(self, period: str = "month") -> dict[str, Any]:
        total = sum(t.get("amount", 0) for t in self._transactions)
        by_category: dict[str, float] = {}
        for t in self._transactions:
            cat = t.get("category", "uncategorized")
            by_category[cat] = by_category.get(cat, 0) + t.get("amount", 0)
        return {
            "period": period,
            "total_spending": total,
            "transaction_count": len(self._transactions),
            "by_category": by_category,
        }
