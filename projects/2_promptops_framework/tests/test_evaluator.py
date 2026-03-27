"""Tests for the PromptEvaluator."""
import pytest
from src.services.evaluator import PromptEvaluator
from src.services.metrics import ExactMatchMetric, ContainsMetric


class TestPromptEvaluator:
    def test_evaluate_exact_match(self):
        evaluator = PromptEvaluator(metrics=[ExactMatchMetric()])
        scores = evaluator.evaluate(["a", "b"], ["a", "c"])
        assert scores["exact_match"] == 0.5

    def test_evaluate_multiple_metrics(self):
        evaluator = PromptEvaluator(
            metrics=[ExactMatchMetric(), ContainsMetric()]
        )
        scores = evaluator.evaluate(["hello world"], ["hello"])
        assert "exact_match" in scores
        assert "contains" in scores
        assert scores["contains"] == 1.0

    def test_evaluate_length_mismatch(self):
        evaluator = PromptEvaluator(metrics=[ExactMatchMetric()])
        with pytest.raises(ValueError):
            evaluator.evaluate(["a"], ["a", "b"])

    def test_evaluate_no_metrics(self):
        evaluator = PromptEvaluator()
        scores = evaluator.evaluate(["a"], ["a"])
        assert scores == {}

    def test_add_metric(self):
        evaluator = PromptEvaluator()
        evaluator.add_metric(ExactMatchMetric())
        scores = evaluator.evaluate(["a"], ["a"])
        assert scores["exact_match"] == 1.0
