"""
Abstract interface for transaction data access in the Personal Finance Agent.

Design Principles:
    - Dependency Inversion Principle (DIP): The API routes and agent tools
      depend on this abstraction rather than on a concrete data store.  This
      makes it straightforward to swap a mock in-memory store for a real
      database-backed implementation without touching business logic.
    - Single Responsibility Principle (SRP): This interface is concerned only
      with CRUD operations on transactions; higher-level analytics belong in
      ``IInsightGenerator``.
    - Liskov Substitution Principle (LSP): Any conforming subclass (mock,
      SQLite, PostgreSQL) can be used wherever ``ITransactionService`` is
      expected.
"""

from abc import ABC, abstractmethod
from typing import Any


class ITransactionService(ABC):
    """Contract for services that manage financial transactions.

    Every concrete implementation must support retrieving, adding, and
    summarizing transactions.  The interface uses plain ``dict`` objects for
    flexibility; a production system could replace these with Pydantic models
    while keeping the same method signatures.
    """

    @abstractmethod
    def get_transactions(
        self, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Retrieve a paginated list of transactions.

        Args:
            limit: Maximum number of transactions to return.
            offset: Number of transactions to skip (for pagination).

        Returns:
            A list of transaction dictionaries.
        """
        ...

    @abstractmethod
    def add_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Persist a new transaction.

        Args:
            transaction: A dictionary with at least ``amount``; may also
                include ``category`` and ``description``.

        Returns:
            The stored transaction dictionary, enriched with a generated
            ``id`` and any server-side defaults.
        """
        ...

    @abstractmethod
    def get_summary(self, period: str = "month") -> dict[str, Any]:
        """Compute an aggregate spending summary for the given period.

        Args:
            period: The time window to summarize (e.g., ``"month"``,
                ``"week"``).

        Returns:
            A dictionary containing ``total_spending``,
            ``transaction_count``, ``by_category``, and ``period``.
        """
        ...
