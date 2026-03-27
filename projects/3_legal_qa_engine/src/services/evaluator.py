"""Evaluator for legal model outputs (SRP)."""
from dataclasses import dataclass


@dataclass
class EvalResult:
    """Evaluation results for a model."""
    accuracy: float
    risk_precision: float
    risk_recall: float


class LegalEvaluator:
    """Evaluates legal model predictions against ground truth."""

    def evaluate(
        self,
        predictions: list[dict[str, str]],
        ground_truth: list[dict[str, str]],
    ) -> EvalResult:
        """Compute accuracy and risk detection metrics."""
        if not predictions or not ground_truth:
            return EvalResult(accuracy=0.0, risk_precision=0.0, risk_recall=0.0)

        correct = 0
        risk_tp = 0
        risk_fp = 0
        risk_fn = 0

        for pred, truth in zip(predictions, ground_truth):
            pred_risk = pred.get("risk_level", "low")
            true_risk = truth.get("risk_level", "low")

            if pred_risk == true_risk:
                correct += 1

            is_risky_pred = pred_risk in ("high", "medium")
            is_risky_true = true_risk in ("high", "medium")

            if is_risky_pred and is_risky_true:
                risk_tp += 1
            elif is_risky_pred and not is_risky_true:
                risk_fp += 1
            elif not is_risky_pred and is_risky_true:
                risk_fn += 1

        n = min(len(predictions), len(ground_truth))
        accuracy = correct / n if n else 0.0
        precision = risk_tp / (risk_tp + risk_fp) if (risk_tp + risk_fp) else 0.0
        recall = risk_tp / (risk_tp + risk_fn) if (risk_tp + risk_fn) else 0.0

        return EvalResult(
            accuracy=accuracy,
            risk_precision=precision,
            risk_recall=recall,
        )
