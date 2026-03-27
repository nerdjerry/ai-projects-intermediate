"""Transaction service interface."""
from abc import ABC, abstractmethod
from typing import Any


class ITransactionService(ABC):
    """Interface for transaction data access (DIP)."""

    @abstractmethod
    def get_transactions(
        self, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Retrieve transactions with pagination."""
        ...

    @abstractmethod
    def add_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Add a new transaction."""
        ...

    @abstractmethod
    def get_summary(self, period: str = "month") -> dict[str, Any]:
        """Get spending summary for a period."""
        ...
