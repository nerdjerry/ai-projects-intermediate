"""
Memory interfaces for the Personal Finance Agent, split into read and write
concerns following the Interface Segregation Principle (ISP).

Design Principles:
    - Interface Segregation Principle (ISP): Clients that only need to *read*
      memories depend on ``IMemoryReader``; clients that only need to *write*
      depend on ``IMemoryWriter``.  This prevents unnecessary coupling — for
      example, a reporting component never needs ``store()`` or ``clear()``.
    - Dependency Inversion Principle (DIP): Concrete storage backends
      (in-memory, Redis, database) implement these abstractions so upper
      layers remain storage-agnostic.
    - Single Responsibility Principle (SRP): Each interface addresses a single
      axis of responsibility (reading vs. writing).

A concrete class may implement *both* interfaces when full read-write access
is appropriate (see ``SessionMemory``).
"""

from abc import ABC, abstractmethod
from typing import Any


class IMemoryReader(ABC):
    """Read-only view of the agent's memory store (ISP).

    Components that only need to look up past interactions or search stored
    context should depend on this interface alone, keeping their coupling
    minimal.
    """

    @abstractmethod
    def recall(self, key: str) -> Any | None:
        """Retrieve a single memory entry by its exact key.

        Args:
            key: The identifier used when the entry was stored.

        Returns:
            The stored value, or ``None`` if the key does not exist.
        """
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search memories using a free-text query.

        Args:
            query: A search string to match against keys and values.
            limit: Maximum number of results to return.

        Returns:
            A list of dictionaries with ``key`` and ``value`` entries.
        """
        ...


class IMemoryWriter(ABC):
    """Write-only view of the agent's memory store (ISP).

    Components that need to persist context (e.g., the conversation manager)
    depend on this interface without gaining read access.
    """

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Persist a memory entry under the given key.

        Args:
            key: A unique identifier for the entry.
            value: The data to store (may be any serializable type).
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from the memory store."""
        ...
