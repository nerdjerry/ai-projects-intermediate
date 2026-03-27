"""
Abstract base class for agent tools in the Personal Finance Agent.

Design Principles:
    - Open/Closed Principle (OCP): New tools (e.g., a budgeting tool, an
      investment analyzer) can be added by creating new subclasses of
      ``AgentTool`` without modifying the agent or any existing tool code.
    - Dependency Inversion Principle (DIP): The agent depends on this
      abstraction rather than on concrete tool implementations, allowing
      tools to be swapped, extended, or mocked independently.
    - Strategy Pattern: Each tool encapsulates a specific capability that
      the agent can invoke at runtime.
"""

from abc import ABC, abstractmethod
from typing import Any


class AgentTool(ABC):
    """Abstract base class that every agent-callable tool must implement.

    The agent discovers available tools via their ``name`` and ``description``
    properties, then delegates work through the ``execute`` method.  This
    contract lets the agent remain closed to modification while staying open
    to extension (OCP) — simply subclass ``AgentTool`` and register the new
    tool with the agent.

    Attributes are exposed as abstract *properties* (not plain attributes) so
    that each concrete tool must explicitly declare its identity.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return a unique, machine-friendly identifier for this tool.

        The agent uses this name to select the correct tool when fulfilling
        a user request.
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable summary of what this tool does.

        The agent may present this description to an LLM so it can decide
        which tool to invoke.
        """
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool's logic and return a plain-text result.

        Args:
            **kwargs: Arbitrary keyword arguments specific to each tool
                (e.g., ``period="month"`` for a spending summary tool).

        Returns:
            A string containing the tool's output, suitable for display
            to the user or further processing by the agent.
        """
        ...
