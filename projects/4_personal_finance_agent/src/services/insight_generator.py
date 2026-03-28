"""
Rule-based financial insight generator.

This module provides a concrete implementation of ``IInsightGenerator``
that analyzes transaction data using simple heuristic rules.

Design Principles:
    - Single Responsibility Principle (SRP): This class's only job is to
      derive human-readable insights from raw transaction data.
    - Liskov Substitution Principle (LSP): ``SimpleInsightGenerator`` can be
      seamlessly replaced with an LLM-powered generator wherever
      ``IInsightGenerator`` is expected — no caller changes needed.
    - Open/Closed Principle (OCP): Additional insight rules can be added to
      ``generate_insights`` without modifying the interface contract.
"""

from typing import Any

from ..interfaces.insight_generator import IInsightGenerator


class SimpleInsightGenerator(IInsightGenerator):
    """Generates spending insights using deterministic rules.

    This implementation is intentionally lightweight and does not require
    an API key or ML model.  In production, you could swap it for an
    LLM-backed generator via Dependency Injection (DIP) — the rest of
    the application would remain unchanged.
    """

    async def generate_insights(
        self, transactions: list[dict[str, Any]]
    ) -> list[str]:
        """Analyze transactions and return a list of insight strings.

        The current rule set includes:
        1. **Top category** — identifies the highest-spending category.
        2. **High-average alert** — warns when the average transaction
           exceeds $100.
        3. **Total summary** — reports aggregate spending and count.

        Args:
            transactions: List of transaction dicts with ``amount`` and
                optional ``category`` keys.

        Returns:
            A list of plain-text insight strings.
        """
        # Handle the trivial case of no data
        if not transactions:
            return ["No transactions to analyze."]

        insights: list[str] = []
        total = sum(t.get("amount", 0) for t in transactions)

        # --- Rule 1: Category breakdown ---
        # Aggregate spending per category so we can identify the top one.
        by_category: dict[str, float] = {}
        for t in transactions:
            cat = t.get("category", "uncategorized")
            by_category[cat] = by_category.get(cat, 0) + t.get("amount", 0)

        if by_category:
            # Determine the category with the highest total spend
            top_cat = max(by_category, key=by_category.get)  # type: ignore[arg-type]
            insights.append(
                f"Your highest spending category is '{top_cat}' "
                f"at ${by_category[top_cat]:.2f}."
            )

        # --- Rule 2: Spending alert ---
        # Flag unusually high average spending for user awareness.
        avg_amount = total / len(transactions) if transactions else 0
        if avg_amount > 100:
            insights.append(
                f"Your average transaction is ${avg_amount:.2f}. "
                "Consider reviewing large purchases."
            )

        # --- Rule 3: Total summary ---
        insights.append(f"Total spending: ${total:.2f} across {len(transactions)} transactions.")
        return insights
