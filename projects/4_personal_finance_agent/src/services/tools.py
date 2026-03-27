"""
Concrete agent tools for the Personal Finance Agent.

Each class in this module extends ``AgentTool`` to provide a specific
capability that the agent can invoke at runtime.

Design Principles:
    - Open/Closed Principle (OCP): New tools are added by creating a new
      subclass of ``AgentTool`` — no existing tool or agent code needs to
      be modified.
    - Dependency Inversion Principle (DIP): Tools receive an
      ``ITransactionService`` through constructor injection, so they remain
      decoupled from any specific data-access implementation.
    - Single Responsibility Principle (SRP): Each tool class encapsulates
      exactly one piece of agent functionality (spending summary *or*
      category breakdown).
    - Strategy Pattern: The agent holds a registry of ``AgentTool``
      instances and selects the right one based on the user's request.
"""

from typing import Any

from ..interfaces.agent_tool import AgentTool
from ..interfaces.transaction_service import ITransactionService


class SpendingSummaryTool(AgentTool):
    """Agent tool that retrieves a spending summary for a given period.

    This tool delegates to the injected ``ITransactionService`` to fetch
    aggregate spending data, demonstrating DIP — the tool never knows
    whether it is talking to a mock or a real database.
    """

    def __init__(self, tx_service: ITransactionService):
        """Initialize with a transaction service dependency.

        Args:
            tx_service: The service used to query spending data (DIP).
        """
        self._tx = tx_service

    @property
    def name(self) -> str:
        """Unique identifier used by the agent to select this tool."""
        return "spending_summary"

    @property
    def description(self) -> str:
        """Human-readable description shown to users or LLMs."""
        return "Get a summary of spending for a given period"

    async def execute(self, **kwargs: Any) -> str:
        """Fetch and format a spending summary.

        Args:
            **kwargs: Accepts an optional ``period`` key (default: ``"month"``).

        Returns:
            A formatted string with period, total spend, and transaction count.
        """
        period = kwargs.get("period", "month")
        summary = self._tx.get_summary(period)
        return (
            f"Period: {summary['period']}, "
            f"Total: ${summary['total_spending']:.2f}, "
            f"Transactions: {summary['transaction_count']}"
        )


class CategoryBreakdownTool(AgentTool):
    """Agent tool that breaks down spending by category.

    Like ``SpendingSummaryTool``, this tool depends on ``ITransactionService``
    (DIP) and focuses on a single responsibility: presenting per-category
    spending figures (SRP).
    """

    def __init__(self, tx_service: ITransactionService):
        """Initialize with a transaction service dependency.

        Args:
            tx_service: The service used to query spending data (DIP).
        """
        self._tx = tx_service

    @property
    def name(self) -> str:
        """Unique identifier used by the agent to select this tool."""
        return "category_breakdown"

    @property
    def description(self) -> str:
        """Human-readable description shown to users or LLMs."""
        return "Get spending breakdown by category"

    async def execute(self, **kwargs: Any) -> str:
        """Fetch category-level spending data and format it for display.

        Args:
            **kwargs: Currently unused; reserved for future filters.

        Returns:
            A multi-line string listing each category and its total spend,
            or a fallback message when no data is available.
        """
        summary = self._tx.get_summary()
        categories = summary.get("by_category", {})
        if not categories:
            return "No spending data available."
        # Sort alphabetically for consistent, readable output
        lines = [f"  {cat}: ${amt:.2f}" for cat, amt in sorted(categories.items())]
        return "Spending by category:\n" + "\n".join(lines)
