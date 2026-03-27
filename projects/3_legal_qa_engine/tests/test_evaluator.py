"""Tests for the LegalEvaluator."""
import pytest
from src.services.evaluator import LegalEvaluator


class TestLegalEvaluator:
    def setup_method(self):
        self.evaluator = LegalEvaluator()

    def test_perfect_accuracy(self):
        preds = [{"risk_level": "high"}, {"risk_level": "low"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.accuracy == 1.0

    def test_zero_accuracy(self):
        preds = [{"risk_level": "high"}]
        truth = [{"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.accuracy == 0.0

    def test_risk_precision(self):
        preds = [{"risk_level": "high"}, {"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.risk_precision == 0.5

    def test_risk_recall(self):
        preds = [{"risk_level": "low"}, {"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "high"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.risk_recall == 0.5

    def test_empty_inputs(self):
        result = self.evaluator.evaluate([], [])
        assert result.accuracy == 0.0

    def test_length_mismatch_raises(self):
        preds = [{"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        with pytest.raises(ValueError, match="same length"):
            self.evaluator.evaluate(preds, truth)
