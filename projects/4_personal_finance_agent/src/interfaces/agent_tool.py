"""Abstract agent tool — add new tools without modifying agent (OCP)."""
from abc import ABC, abstractmethod
from typing import Any


class AgentTool(ABC):
    """Abstract tool that an agent can use (DIP + OCP)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for the agent."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the agent."""
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool and return a string result."""
        ...
