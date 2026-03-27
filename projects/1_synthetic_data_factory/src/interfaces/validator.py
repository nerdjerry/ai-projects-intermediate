"""Validator interface for data quality checks."""
from abc import ABC, abstractmethod


class IValidator(ABC):
    """Interface for dataset validation."""

    @abstractmethod
    def validate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Validate and filter records, returning only valid ones."""
        ...

    @abstractmethod
    def deduplicate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove duplicate records."""
        ...
