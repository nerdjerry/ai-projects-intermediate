"""
Evaluator for legal model outputs.

This module contains ``LegalEvaluator``, which computes accuracy and
risk-detection metrics (precision & recall) by comparing model
predictions against ground-truth labels.

**SOLID – Single Responsibility Principle (SRP):**
    "A class should have one, and only one, reason to change."

``LegalEvaluator`` changes only when evaluation logic changes — not
when the model, the dataset format, or the API changes. Keeping
evaluation in its own class also makes it easy to unit-test in
isolation (see ``tests/test_evaluator.py``).

**Design decision:** The evaluator is intentionally stateless —
``evaluate()`` is a pure function that takes inputs and returns an
``EvalResult``, with no side effects. This makes it straightforward
to run in parallel or in a CI pipeline.
"""
from dataclasses import dataclass


@dataclass
class EvalResult:
    """Evaluation results for a model.

    Attributes:
        accuracy: Fraction of predictions whose ``risk_level`` exactly
                  matches the ground truth (range 0.0 – 1.0).
        risk_precision: Of all items the model flagged as risky
                        (high/medium), what fraction truly are risky.
        risk_recall: Of all truly risky items, what fraction did the
                     model correctly flag.
    """
    accuracy: float
    risk_precision: float
    risk_recall: float


class LegalEvaluator:
    """Evaluates legal model predictions against ground truth.

    **SRP in practice:** This class does exactly one thing — compute
    evaluation metrics. It does not load data, build datasets, or
    call the model.

    **Metrics explained (for learners):**
        • **Accuracy** — simple proportion of correct predictions.
        • **Precision** — "When the model says risky, is it right?"
          ``TP / (TP + FP)``
        • **Recall** — "Of all actual risks, how many did the model catch?"
          ``TP / (TP + FN)``

    These metrics are standard in binary/multi-class classification
    tasks and are especially important in the legal domain where
    missing a risk (low recall) can have serious consequences.
    """

    def evaluate(
        self,
        predictions: list[dict[str, str]],
        ground_truth: list[dict[str, str]],
    ) -> EvalResult:
        """Compute accuracy and risk detection metrics.

        Args:
            predictions: Model outputs, each dict must contain a
                         ``risk_level`` key.
            ground_truth: Expected labels in the same format.

        Returns:
            An ``EvalResult`` dataclass with accuracy, precision,
            and recall.

        Raises:
            ValueError: If predictions and ground_truth have different lengths.
        """
        # Handle the degenerate case of empty inputs gracefully.
        if not predictions or not ground_truth:
            return EvalResult(accuracy=0.0, risk_precision=0.0, risk_recall=0.0)

        if len(predictions) != len(ground_truth):
            raise ValueError(
                f"predictions and ground_truth must have the same length, "
                f"got {len(predictions)} and {len(ground_truth)}"
            )

        correct = 0
        # Confusion-matrix counters for the "risky" class.
        risk_tp = 0  # True Positives  — predicted risky AND truly risky
        risk_fp = 0  # False Positives — predicted risky BUT actually safe
        risk_fn = 0  # False Negatives — predicted safe BUT actually risky

        for pred, truth in zip(predictions, ground_truth):
            pred_risk = pred.get("risk_level", "low")
            true_risk = truth.get("risk_level", "low")

            # Exact-match accuracy across all risk levels.
            if pred_risk == true_risk:
                correct += 1

            # Binary classification: "risky" = high or medium vs. "safe" = low.
            is_risky_pred = pred_risk in ("high", "medium")
            is_risky_true = true_risk in ("high", "medium")

            if is_risky_pred and is_risky_true:
                risk_tp += 1
            elif is_risky_pred and not is_risky_true:
                risk_fp += 1
            elif not is_risky_pred and is_risky_true:
                risk_fn += 1

        n = len(predictions)
        accuracy = correct / n
        # Guard against division by zero when no risky predictions exist.
        precision = risk_tp / (risk_tp + risk_fp) if (risk_tp + risk_fp) else 0.0
        recall = risk_tp / (risk_tp + risk_fn) if (risk_tp + risk_fn) else 0.0

        return EvalResult(
            accuracy=accuracy,
            risk_precision=precision,
            risk_recall=recall,
        )
