"""
Evaluator interface — open for new metrics (OCP).

This module defines two complementary abstractions:

1. ``IEvaluator`` — orchestrates scoring of model outputs.
2. ``IMetric``    — represents a single, pluggable evaluation metric.

Together they demonstrate the **Open/Closed Principle (OCP)**: you can
introduce entirely new scoring strategies (e.g. BLEU, ROUGE, cosine
similarity) by implementing ``IMetric`` — *without* touching the evaluator
or any existing metric class.

The split into two interfaces also follows the **Interface Segregation
Principle (ISP)**: consumers that only need to compute a single score depend
on ``IMetric``, while higher-level orchestrators depend on ``IEvaluator``.

Design decisions
----------------
* ``IMetric.name`` is a read-only ``@property`` so every metric is forced to
  declare a human-readable identifier — used as a dictionary key in results.
* ``compute`` works on a *single* prediction/reference pair.  Aggregation
  (averaging) is the evaluator's responsibility — this keeps each metric
  focused on one thing (**SRP**).
"""

from abc import ABC, abstractmethod
from typing import Any


class IEvaluator(ABC):
    """Abstract interface for prompt-output evaluation.

    An evaluator receives parallel lists of predictions and ground-truth
    references and returns a dictionary mapping metric names to their
    aggregate scores.

    Implementing this interface lets you swap evaluation strategies (e.g.
    weighted scoring, statistical tests) without affecting calling code —
    a direct benefit of the **Dependency Inversion Principle (DIP)**.
    """

    @abstractmethod
    def evaluate(
        self, predictions: list[str], references: list[str], **kwargs: Any
    ) -> dict[str, float]:
        """Score *predictions* against *references*.

        Parameters
        ----------
        predictions : list[str]
            Model-generated outputs to evaluate.
        references : list[str]
            Ground-truth outputs to compare against.
        **kwargs : Any
            Optional configuration forwarded to individual metrics.

        Returns
        -------
        dict[str, float]
            Mapping of metric name → aggregate score.
        """
        ...


class IMetric(ABC):
    """Abstract interface for a single evaluation metric.

    Each metric encapsulates *one* way of comparing a prediction to a
    reference.  New metrics can be added by subclassing ``IMetric`` without
    modifying the evaluator — this is the **Open/Closed Principle (OCP)** in
    action.

    Because every ``IMetric`` subclass must honour the same contract (return a
    float in a consistent range), any subclass can stand in for ``IMetric``
    transparently — satisfying the **Liskov Substitution Principle (LSP)**.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable metric name, used as the key in result dicts."""
        ...

    @abstractmethod
    def compute(self, prediction: str, reference: str) -> float:
        """Compute a score for a single prediction/reference pair.

        Parameters
        ----------
        prediction : str
            A single model-generated output.
        reference : str
            The corresponding ground-truth output.

        Returns
        -------
        float
            A numeric score (typically 0.0–1.0, but not strictly required).
        """
        ...
