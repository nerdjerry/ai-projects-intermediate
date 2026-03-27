"""Tests for the SimpleInsightGenerator."""
import pytest
from src.services.insight_generator import SimpleInsightGenerator


class TestSimpleInsightGenerator:
    def setup_method(self):
        self.gen = SimpleInsightGenerator()

    @pytest.mark.asyncio
    async def test_no_transactions(self):
        insights = await self.gen.generate_insights([])
        assert len(insights) == 1
        assert "No transactions" in insights[0]

    @pytest.mark.asyncio
    async def test_basic_insights(self):
        txns = [
            {"amount": 50.0, "category": "food"},
            {"amount": 30.0, "category": "transport"},
        ]
        insights = await self.gen.generate_insights(txns)
        assert len(insights) >= 1
        assert any("food" in i for i in insights)

    @pytest.mark.asyncio
    async def test_high_spending_alert(self):
        txns = [{"amount": 500.0, "category": "luxury"}]
        insights = await self.gen.generate_insights(txns)
        assert any("average" in i.lower() or "review" in i.lower() for i in insights)
