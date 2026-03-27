"""Evaluator interface — open for new metrics (OCP)."""
from abc import ABC, abstractmethod
from typing import Any


class IEvaluator(ABC):
    """Interface for prompt evaluation."""

    @abstractmethod
    def evaluate(
        self, predictions: list[str], references: list[str], **kwargs: Any
    ) -> dict[str, float]:
        """Score predictions against references."""
        ...


class IMetric(ABC):
    """Single metric — add new metrics without modifying evaluator (OCP)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable metric name."""
        ...

    @abstractmethod
    def compute(self, prediction: str, reference: str) -> float:
        """Compute score for a single prediction/reference pair."""
        ...
