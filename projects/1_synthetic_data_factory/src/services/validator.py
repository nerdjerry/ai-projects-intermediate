"""Concrete validator for Q&A dataset quality (SRP: validation only).

This module implements the ``IValidator`` interface with simple but
effective quality rules: minimum-length filtering and exact-duplicate
removal.  Because validation is isolated here, the generation and
storage layers remain blissfully unaware of quality criteria.

Design principles:
  - SRP (Single Responsibility Principle): This class does one thing —
    decide whether records are "good enough".  Generation and persistence
    are handled by other services.
  - LSP (Liskov Substitution Principle): ``DataValidator`` can be used
    wherever an ``IValidator`` is expected.  A stricter or ML-based
    validator could replace it without breaking callers.
  - OCP (Open/Closed Principle): To change quality rules, create a new
    ``IValidator`` implementation rather than editing this one.
"""
from ..interfaces.validator import IValidator


class DataValidator(IValidator):
    """Validates and cleans generated Q&A records.

    Quality criteria are intentionally simple for this project:
      * Both ``question`` and ``answer`` must meet a configurable minimum
        character length.
      * Exact-duplicate questions are removed (first occurrence wins).
    """

    def __init__(self, min_length: int = 10):
        """Initialise the validator with a minimum field length.

        Args:
            min_length: The minimum number of characters required in both
                the ``question`` and ``answer`` fields for a record to
                pass validation.  Defaults to 10.
        """
        self._min_length = min_length

    def validate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Keep records whose question and answer both exceed *min_length*.

        Records with missing keys are handled gracefully via ``dict.get``
        with a default of ``""``, which will always be shorter than any
        reasonable ``min_length`` — so they are filtered out automatically.
        """
        return [
            r
            for r in records
            if len(r.get("question", "")) >= self._min_length
            and len(r.get("answer", "")) >= self._min_length
        ]

    def deduplicate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove exact-duplicate questions, preserving first-seen order.

        Uses a ``set`` for O(1) membership checks.  Only the *question*
        text is considered for deduplication — two records with the same
        question but different answers are treated as duplicates because
        the question is the primary key for Q&A datasets.
        """
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for r in records:
            q = r.get("question", "")
            if q not in seen:
                seen.add(q)
                unique.append(r)
        return unique
