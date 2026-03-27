"""
Abstract interface for generating financial insights.

Design Principles:
    - Single Responsibility Principle (SRP): Insight generation is isolated
      behind its own interface so that the logic for analyzing transactions
      can evolve independently from data retrieval or presentation.
    - Dependency Inversion Principle (DIP): Higher-level modules (e.g., the
      API layer or the agent) depend on this abstraction rather than on any
      specific insight-generation strategy.
    - Liskov Substitution Principle (LSP): Any conforming implementation —
      rule-based, ML-powered, or LLM-backed — can be substituted without
      breaking callers.
"""

from abc import ABC, abstractmethod
from typing import Any


class IInsightGenerator(ABC):
    """Contract for services that derive actionable insights from transactions.

    Implementations might range from simple rule-based heuristics to
    sophisticated LLM-powered analysis.  Callers are shielded from the
    underlying strategy thanks to this abstraction (DIP).
    """

    @abstractmethod
    async def generate_insights(
        self, transactions: list[dict[str, Any]]
    ) -> list[str]:
        """Analyze transactions and produce human-readable insights.

        Args:
            transactions: A list of transaction dictionaries, each containing
                at least ``amount`` and optionally ``category``.

        Returns:
            A list of insight strings (e.g., spending alerts, category
            breakdowns) ready for display to the user.
        """
        ...
