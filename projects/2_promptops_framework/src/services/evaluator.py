"""Concrete evaluator — composes metrics (SRP + OCP)."""
from typing import Any

from ..interfaces.evaluator import IEvaluator, IMetric


class PromptEvaluator(IEvaluator):
    """Evaluates prompt outputs using pluggable metrics."""

    def __init__(self, metrics: list[IMetric] | None = None):
        self._metrics: list[IMetric] = metrics or []

    def add_metric(self, metric: IMetric) -> None:
        """Register a new metric (Open/Closed — extend, don't modify)."""
        self._metrics.append(metric)

    def evaluate(
        self, predictions: list[str], references: list[str], **kwargs: Any
    ) -> dict[str, float]:
        if len(predictions) != len(references):
            raise ValueError("predictions and references must have the same length")
        if not self._metrics:
            return {}
        scores: dict[str, list[float]] = {m.name: [] for m in self._metrics}
        for pred, ref in zip(predictions, references):
            for metric in self._metrics:
                scores[metric.name].append(metric.compute(pred, ref))
        return {
            name: sum(vals) / len(vals) if vals else 0.0
            for name, vals in scores.items()
        }
