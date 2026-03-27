"""Built-in metrics — add new metrics by subclassing IMetric (OCP)."""
from ..interfaces.evaluator import IMetric


class ExactMatchMetric(IMetric):
    """1.0 if prediction exactly matches reference, else 0.0."""

    @property
    def name(self) -> str:
        return "exact_match"

    def compute(self, prediction: str, reference: str) -> float:
        return 1.0 if prediction.strip() == reference.strip() else 0.0


class ContainsMetric(IMetric):
    """1.0 if reference text is contained in the prediction."""

    @property
    def name(self) -> str:
        return "contains"

    def compute(self, prediction: str, reference: str) -> float:
        return 1.0 if reference.strip().lower() in prediction.strip().lower() else 0.0


class LengthRatioMetric(IMetric):
    """Ratio of prediction length to reference length (capped at 1.0)."""

    @property
    def name(self) -> str:
        return "length_ratio"

    def compute(self, prediction: str, reference: str) -> float:
        if not reference:
            return 0.0
        ratio = len(prediction) / len(reference)
        return min(ratio, 1.0)
