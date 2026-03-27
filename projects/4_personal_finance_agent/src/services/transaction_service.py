"""Mock transaction service (SRP — data access only).

This in-memory implementation stores transactions in a list. It satisfies
the ITransactionService interface and can be swapped for a real database-
backed implementation (e.g., PostgreSQL + SQLAlchemy) via the Liskov
Substitution Principle.

Design principles:
  - SRP: Only handles transaction storage and retrieval.
  - LSP: Implements ITransactionService — any code expecting the interface
    can use this mock or a real DB implementation interchangeably.
  - DIP: Callers depend on the abstract ITransactionService, not this class.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from ..interfaces.transaction_service import ITransactionService


class MockTransactionService(ITransactionService):
    """In-memory transaction store (swap for real DB via LSP).

    All transactions are kept in a list. For production use, replace this
    with a class that persists to PostgreSQL/SQLite via SQLAlchemy.
    """

    def __init__(self) -> None:
        """Initialize with an empty transaction list."""
        self._transactions: list[dict[str, Any]] = []

    def add_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Add a new transaction and return it with a generated ID and date.

        Args:
            transaction: Dict with 'amount', optional 'category' and 'description'.

        Returns:
            The complete transaction record with 'id' and 'date' filled in.
        """
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
        """Retrieve transactions with pagination.

        Args:
            limit: Maximum number of transactions to return. Use 0 to fetch all.
            offset: Number of transactions to skip from the start.

        Returns:
            Slice of transactions based on limit and offset.
        """
        if limit == 0:
            return self._transactions[offset:]
        return self._transactions[offset : offset + limit]

    def get_summary(self, period: str = "month") -> dict[str, Any]:
        """Get spending summary across all transactions.

        Computes total spending and per-category breakdown. The 'period'
        parameter is for labeling; in a real implementation it would
        filter transactions by date range.

        Args:
            period: Time period label (e.g., 'month', 'week').

        Returns:
            Dict with total_spending, transaction_count, and by_category.
        """
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
