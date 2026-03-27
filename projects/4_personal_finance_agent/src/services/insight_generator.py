"""Generates financial insights from transactions (SRP)."""
from typing import Any

from ..interfaces.insight_generator import IInsightGenerator


class SimpleInsightGenerator(IInsightGenerator):
    """Rule-based insight generator (swap for LLM-based via LSP)."""

    async def generate_insights(
        self, transactions: list[dict[str, Any]]
    ) -> list[str]:
        if not transactions:
            return ["No transactions to analyze."]

        insights: list[str] = []
        total = sum(t.get("amount", 0) for t in transactions)

        # Category breakdown
        by_category: dict[str, float] = {}
        for t in transactions:
            cat = t.get("category", "uncategorized")
            by_category[cat] = by_category.get(cat, 0) + t.get("amount", 0)

        if by_category:
            top_cat = max(by_category, key=by_category.get)  # type: ignore[arg-type]
            insights.append(
                f"Your highest spending category is '{top_cat}' "
                f"at ${by_category[top_cat]:.2f}."
            )

        # Spending alert
        avg_amount = total / len(transactions) if transactions else 0
        if avg_amount > 100:
            insights.append(
                f"Your average transaction is ${avg_amount:.2f}. "
                "Consider reviewing large purchases."
            )

        insights.append(f"Total spending: ${total:.2f} across {len(transactions)} transactions.")
        return insights
