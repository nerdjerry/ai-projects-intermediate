"""
Concrete evaluator — composes metrics (SRP + OCP).

This module provides the ``PromptEvaluator``, the production implementation
of the ``IEvaluator`` interface.  Its sole job is to *orchestrate* a
collection of ``IMetric`` objects — it never contains metric-specific logic
itself.

Key design patterns & SOLID principles
---------------------------------------
* **Strategy Pattern** — each ``IMetric`` encapsulates a distinct scoring
  algorithm.  The evaluator iterates over whatever metrics it has been given,
  without knowing (or caring) about the details.
* **SRP** — ``PromptEvaluator`` does exactly one thing: aggregate metric
  scores.  Individual scoring logic lives in the metrics.
* **OCP** — adding a brand-new metric (e.g. ``BLEUMetric``) requires zero
  changes to this file; you simply pass the new metric to the evaluator.
* **DIP** — the evaluator depends on the ``IMetric`` *interface*, not on
  concrete metric classes.
"""

from typing import Any

from ..interfaces.evaluator import IEvaluator, IMetric


class PromptEvaluator(IEvaluator):
    """Evaluates prompt outputs by delegating to pluggable ``IMetric`` instances.

    Metrics can be supplied at construction time or added later via
    ``add_metric``.  The evaluator computes per-pair scores for every
    registered metric and returns the arithmetic mean for each.
    """

    def __init__(self, metrics: list[IMetric] | None = None):
        # Store the metrics list; default to empty so callers can add later.
        self._metrics: list[IMetric] = metrics or []

    # -- OCP: new metrics are *added*, the evaluator itself is never modified --
    def add_metric(self, metric: IMetric) -> None:
        """Register a new metric at runtime.

        This is the Open/Closed Principle in action: we *extend* the
        evaluator's capabilities without modifying its existing code.
        """
        self._metrics.append(metric)

    def evaluate(
        self, predictions: list[str], references: list[str], **kwargs: Any
    ) -> dict[str, float]:
        """Score every prediction against its reference using all registered metrics.

        Returns a dict mapping each metric's ``name`` to the average score
        across all prediction/reference pairs.

        Raises
        ------
        ValueError
            If *predictions* and *references* have different lengths.
        """
        # Guard clause — fast feedback for the caller.
        if len(predictions) != len(references):
            raise ValueError("predictions and references must have the same length")

        # No metrics registered → nothing to compute.
        if not self._metrics:
            return {}

        # Collect per-pair scores for every metric.
        scores: dict[str, list[float]] = {m.name: [] for m in self._metrics}
        for pred, ref in zip(predictions, references):
            for metric in self._metrics:
                # Each metric computes its own score (Strategy Pattern).
                scores[metric.name].append(metric.compute(pred, ref))

        # Aggregate: compute the arithmetic mean for each metric.
        return {
            name: sum(vals) / len(vals) if vals else 0.0
            for name, vals in scores.items()
        }
