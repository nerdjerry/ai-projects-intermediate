"""Concrete agent tools (OCP — add new tools by subclassing AgentTool)."""
from typing import Any

from ..interfaces.agent_tool import AgentTool
from ..interfaces.transaction_service import ITransactionService


class SpendingSummaryTool(AgentTool):
    """Summarize spending for a period."""

    def __init__(self, tx_service: ITransactionService):
        self._tx = tx_service

    @property
    def name(self) -> str:
        return "spending_summary"

    @property
    def description(self) -> str:
        return "Get a summary of spending for a given period"

    async def execute(self, **kwargs: Any) -> str:
        period = kwargs.get("period", "month")
        summary = self._tx.get_summary(period)
        return (
            f"Period: {summary['period']}, "
            f"Total: ${summary['total_spending']:.2f}, "
            f"Transactions: {summary['transaction_count']}"
        )


class CategoryBreakdownTool(AgentTool):
    """Break down spending by category."""

    def __init__(self, tx_service: ITransactionService):
        self._tx = tx_service

    @property
    def name(self) -> str:
        return "category_breakdown"

    @property
    def description(self) -> str:
        return "Get spending breakdown by category"

    async def execute(self, **kwargs: Any) -> str:
        summary = self._tx.get_summary()
        categories = summary.get("by_category", {})
        if not categories:
            return "No spending data available."
        lines = [f"  {cat}: ${amt:.2f}" for cat, amt in sorted(categories.items())]
        return "Spending by category:\n" + "\n".join(lines)
