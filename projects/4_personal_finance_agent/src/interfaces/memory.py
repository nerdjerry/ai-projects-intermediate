"""Memory interfaces — separate read/write (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class IMemoryReader(ABC):
    """Read-only memory interface (ISP)."""

    @abstractmethod
    def recall(self, key: str) -> Any | None:
        """Retrieve a memory by key."""
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search memories by query."""
        ...


class IMemoryWriter(ABC):
    """Write-only memory interface (ISP)."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a memory entry."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all memories."""
        ...
