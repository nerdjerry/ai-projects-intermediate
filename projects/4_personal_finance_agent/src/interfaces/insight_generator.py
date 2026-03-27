"""Insight generator interface."""
from abc import ABC, abstractmethod
from typing import Any


class IInsightGenerator(ABC):
    """Interface for generating financial insights (SRP)."""

    @abstractmethod
    async def generate_insights(
        self, transactions: list[dict[str, Any]]
    ) -> list[str]:
        """Generate insights from transaction data."""
        ...
