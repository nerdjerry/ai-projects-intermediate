"""Concrete validator for Q&A dataset quality (SRP: validation only)."""
from ..interfaces.validator import IValidator


class DataValidator(IValidator):
    """Validates and cleans generated Q&A records."""

    def __init__(self, min_length: int = 10):
        self._min_length = min_length

    def validate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Keep records whose question and answer exceed *min_length*."""
        return [
            r
            for r in records
            if len(r.get("question", "")) >= self._min_length
            and len(r.get("answer", "")) >= self._min_length
        ]

    def deduplicate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove exact-duplicate questions."""
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for r in records:
            q = r.get("question", "")
            if q not in seen:
                seen.add(q)
                unique.append(r)
        return unique
