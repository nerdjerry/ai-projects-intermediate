"""
Tests for the ``PromptEvaluator`` service.

This test module verifies the orchestration logic inside ``PromptEvaluator``
— the concrete ``IEvaluator`` implementation that aggregates pluggable
``IMetric`` instances.

What these tests demonstrate for learners
-----------------------------------------
* **Testing the Strategy Pattern** — by injecting different combinations of
  real metrics, we validate that the evaluator correctly delegates scoring
  and averages results.  No mocks are needed because the built-in metrics
  are fast and deterministic.
* **Edge-case coverage** — mismatched list lengths, no metrics registered,
  and runtime metric addition are all explicitly tested.
* **OCP validation** — ``test_add_metric`` proves that the evaluator can be
  *extended* at runtime (via ``add_metric``) without modifying its class.
"""

import pytest
from src.services.evaluator import PromptEvaluator
from src.services.metrics import ExactMatchMetric, ContainsMetric


class TestPromptEvaluator:
    """Unit tests for ``PromptEvaluator``."""

    def test_evaluate_exact_match(self):
        """Average exact-match score should be 0.5 when one of two pairs matches."""
        evaluator = PromptEvaluator(metrics=[ExactMatchMetric()])
        scores = evaluator.evaluate(["a", "b"], ["a", "c"])
        assert scores["exact_match"] == 0.5

    def test_evaluate_multiple_metrics(self):
        """Multiple metrics should each appear in the result dict.

        This validates the Strategy Pattern: the evaluator iterates over all
        registered metrics and returns a score for each.
        """
        evaluator = PromptEvaluator(
            metrics=[ExactMatchMetric(), ContainsMetric()]
        )
        scores = evaluator.evaluate(["hello world"], ["hello"])
        assert "exact_match" in scores
        assert "contains" in scores
        # "hello" is contained in "hello world" → 1.0
        assert scores["contains"] == 1.0

    def test_evaluate_length_mismatch(self):
        """A ``ValueError`` must be raised when list lengths differ.

        This guards against accidental misalignment between predictions and
        references — a common data-handling bug.
        """
        evaluator = PromptEvaluator(metrics=[ExactMatchMetric()])
        with pytest.raises(ValueError):
            evaluator.evaluate(["a"], ["a", "b"])

    def test_evaluate_no_metrics(self):
        """An evaluator with no metrics should return an empty dict, not crash."""
        evaluator = PromptEvaluator()
        scores = evaluator.evaluate(["a"], ["a"])
        assert scores == {}

    def test_add_metric(self):
        """Metrics added at runtime via ``add_metric`` should take effect.

        This is a direct test of the Open/Closed Principle: the evaluator is
        *extended* with a new metric without modifying its source code.
        """
        evaluator = PromptEvaluator()
        evaluator.add_metric(ExactMatchMetric())
        scores = evaluator.evaluate(["a"], ["a"])
        assert scores["exact_match"] == 1.0
