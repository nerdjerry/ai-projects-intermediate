"""
Built-in metrics — add new metrics by subclassing ``IMetric`` (OCP).

This module ships three concrete metrics that learners can use out of the
box: ``ExactMatchMetric``, ``ContainsMetric``, and ``LengthRatioMetric``.

Each class is a self-contained implementation of the ``IMetric`` interface.
Because every metric follows the same contract (``name`` property + ``compute``
method), the ``PromptEvaluator`` can treat them interchangeably — a practical
demonstration of the **Liskov Substitution Principle (LSP)**.

Want to add a new metric (e.g. BLEU, ROUGE, cosine-similarity)?
Just create another ``IMetric`` subclass in this file (or anywhere else) and
pass it to the evaluator.  No existing code needs to change — that is the
**Open/Closed Principle (OCP)** at work.
"""

from ..interfaces.evaluator import IMetric


class ExactMatchMetric(IMetric):
    """Binary metric: 1.0 if the prediction exactly equals the reference.

    Leading/trailing whitespace is stripped before comparison so that minor
    formatting differences don't cause false negatives.

    LSP note: this class is fully substitutable for ``IMetric`` — it honours
    the expected signature and return-type contract.
    """

    @property
    def name(self) -> str:  # noqa: D401 — short imperative name
        return "exact_match"

    def compute(self, prediction: str, reference: str) -> float:
        """Return 1.0 on exact match (after stripping whitespace), else 0.0."""
        return 1.0 if prediction.strip() == reference.strip() else 0.0


class ContainsMetric(IMetric):
    """Checks whether the *reference* text appears anywhere in the prediction.

    The comparison is case-insensitive and whitespace-trimmed, making it
    useful for checking that a model's free-form answer includes a required
    keyword or phrase.
    """

    @property
    def name(self) -> str:
        return "contains"

    def compute(self, prediction: str, reference: str) -> float:
        """Return 1.0 if *reference* is a substring of *prediction* (case-insensitive)."""
        return 1.0 if reference.strip().lower() in prediction.strip().lower() else 0.0


class LengthRatioMetric(IMetric):
    """Measures how close the prediction's length is to the reference's length.

    The score is ``min(len(prediction) / len(reference), 1.0)``, so a
    prediction that is shorter than the reference receives a proportional
    score, while a prediction that is longer is capped at 1.0.

    This is a simple proxy for verbosity/conciseness and is useful when you
    want the model's output to be roughly the same length as the expected
    answer.
    """

    @property
    def name(self) -> str:
        return "length_ratio"

    def compute(self, prediction: str, reference: str) -> float:
        """Return the length ratio, capped at 1.0.  Returns 0.0 for empty references."""
        if not reference:
            # Avoid division-by-zero; an empty reference is undefined.
            return 0.0
        ratio = len(prediction) / len(reference)
        return min(ratio, 1.0)
