"""
In-memory session memory for the Personal Finance Agent.

This module provides ``SessionMemory``, a lightweight dictionary-backed
implementation of the memory interfaces defined in
``src.interfaces.memory``.

Design Principles:
    - Single Responsibility Principle (SRP): This class is solely responsible
      for storing and retrieving key-value memory entries; it does not
      perform serialization, persistence, or analytics.
    - Liskov Substitution Principle (LSP): ``SessionMemory`` implements both
      ``IMemoryReader`` **and** ``IMemoryWriter``, so it can replace any
      component that expects either interface without side effects.
    - Interface Segregation Principle (ISP): By inheriting from *two* narrow
      interfaces (rather than one wide one), the class lets callers depend
      only on the slice of functionality they actually need.
    - Dependency Inversion Principle (DIP): Upper layers receive a
      ``SessionMemory`` through constructor injection as an
      ``IMemoryReader`` or ``IMemoryWriter``, remaining agnostic of the
      storage mechanism.
"""

from typing import Any

from ..interfaces.memory import IMemoryReader, IMemoryWriter


class SessionMemory(IMemoryReader, IMemoryWriter):
    """Ephemeral, dictionary-backed memory store for a single user session.

    This class implements both the read and write memory interfaces (ISP),
    making it suitable for components that need full access.  Components
    that only need to *read* can accept ``IMemoryReader`` instead, and
    those that only need to *write* can accept ``IMemoryWriter``.
    """

    def __init__(self) -> None:
        """Initialize an empty memory store."""
        # Internal dictionary that maps string keys to arbitrary values.
        self._store: dict[str, Any] = {}

    # --- IMemoryReader implementation ---

    def recall(self, key: str) -> Any | None:
        """Look up a memory entry by exact key.

        Args:
            key: The identifier to look up.

        Returns:
            The stored value, or ``None`` if absent.
        """
        return self._store.get(key)

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Perform a case-insensitive substring search over keys and values.

        This is a simple linear scan — adequate for session-sized data.
        A production implementation might use vector embeddings for
        semantic search.

        Args:
            query: The substring to search for.
            limit: Maximum number of matches to return.

        Returns:
            A list of ``{"key": ..., "value": ...}`` dictionaries.
        """
        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        for key, value in self._store.items():
            # Match against both the key and the stringified value
            if query_lower in key.lower() or query_lower in str(value).lower():
                results.append({"key": key, "value": value})
                if len(results) >= limit:
                    break
        return results

    # --- IMemoryWriter implementation ---

    def store(self, key: str, value: Any) -> None:
        """Store or overwrite a memory entry.

        Args:
            key: Unique identifier for the entry.
            value: Data to persist.
        """
        self._store[key] = value

    def clear(self) -> None:
        """Remove all entries, resetting the memory to an empty state."""
        self._store.clear()

    # --- Convenience property (not part of the interface) ---

    @property
    def size(self) -> int:
        """Return the number of entries currently in the store."""
        return len(self._store)
