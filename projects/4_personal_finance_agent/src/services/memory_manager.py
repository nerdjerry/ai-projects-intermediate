"""In-memory implementation of memory interfaces (SRP + LSP)."""
from typing import Any

from ..interfaces.memory import IMemoryReader, IMemoryWriter


class SessionMemory(IMemoryReader, IMemoryWriter):
    """Short-term session memory (in-memory dict)."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def recall(self, key: str) -> Any | None:
        return self._store.get(key)

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        for key, value in self._store.items():
            if query_lower in key.lower() or query_lower in str(value).lower():
                results.append({"key": key, "value": value})
                if len(results) >= limit:
                    break
        return results

    def store(self, key: str, value: Any) -> None:
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)
