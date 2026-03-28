"""
Tests for ``SimpleInsightGenerator``.

These tests verify the rule-based insight engine without touching any
external service, confirming that the class honours its
``IInsightGenerator`` contract (LSP).

Testing Strategy:
    - **Empty input**: Ensures a graceful fallback message.
    - **Basic insights**: Validates category identification in output.
    - **High-spending alert**: Confirms the threshold-based warning fires
      when the average exceeds $100.
"""

import pytest
from src.services.insight_generator import SimpleInsightGenerator


class TestSimpleInsightGenerator:
    """Unit tests for the SimpleInsightGenerator rule-based engine."""

    def setup_method(self):
        """Create a fresh generator instance for each test (test isolation)."""
        self.gen = SimpleInsightGenerator()

    @pytest.mark.asyncio
    async def test_no_transactions(self):
        """An empty transaction list should return a single 'no data' message."""
        insights = await self.gen.generate_insights([])
        assert len(insights) == 1
        assert "No transactions" in insights[0]

    @pytest.mark.asyncio
    async def test_basic_insights(self):
        """Given categorized transactions, the top category should appear."""
        txns = [
            {"amount": 50.0, "category": "food"},
            {"amount": 30.0, "category": "transport"},
        ]
        insights = await self.gen.generate_insights(txns)
        # At least the total-summary insight must be present
        assert len(insights) >= 1
        # 'food' is the highest spend — it should be mentioned
        assert any("food" in i for i in insights)

    @pytest.mark.asyncio
    async def test_high_spending_alert(self):
        """When average spend exceeds $100, a review warning should appear."""
        txns = [{"amount": 500.0, "category": "luxury"}]
        insights = await self.gen.generate_insights(txns)
        # Look for the average-spending alert in the output
        assert any("average" in i.lower() or "review" in i.lower() for i in insights)
