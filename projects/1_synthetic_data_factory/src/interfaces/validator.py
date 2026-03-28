"""Validator interface for data quality checks.

This module defines the abstract contract for validating and deduplicating
generated Q&A records.  Keeping validation behind an interface allows the
pipeline to swap validation strategies (strict, lenient, ML-based) without
modifying the code that *uses* the validator.

Design principles:
  - SRP (Single Responsibility Principle): Validation logic lives in its
    own interface and implementations — generation and storage know nothing
    about quality rules.
  - ISP (Interface Segregation Principle): Only validation-related methods
    appear here.  Classes that only need to generate or store data are not
    forced to implement validation.
  - DIP (Dependency Inversion Principle): Higher-level orchestration code
    (e.g. API routes) can depend on ``IValidator`` rather than a concrete
    ``DataValidator``, making the system easier to test and extend.
"""
from abc import ABC, abstractmethod


class IValidator(ABC):
    """Interface for dataset validation and deduplication.

    Concrete implementations define their own quality criteria (minimum
    length, format checks, semantic similarity for dedup, etc.).  The
    pipeline only calls ``validate`` and ``deduplicate``, remaining
    agnostic to the specific rules applied.
    """

    @abstractmethod
    def validate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Return only records that meet the quality criteria.

        Args:
            records: Raw Q&A dictionaries to evaluate.

        Returns:
            A filtered list containing only records deemed valid.
        """
        ...

    @abstractmethod
    def deduplicate(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove duplicate records from the list.

        Args:
            records: Potentially duplicated Q&A dictionaries.

        Returns:
            A deduplicated list preserving the original order.
        """
        ...
