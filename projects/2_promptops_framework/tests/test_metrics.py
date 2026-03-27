"""Tests for the built-in metrics."""
from src.services.metrics import ExactMatchMetric, ContainsMetric, LengthRatioMetric


class TestExactMatchMetric:
    def setup_method(self):
        self.metric = ExactMatchMetric()

    def test_exact_match(self):
        assert self.metric.compute("hello", "hello") == 1.0

    def test_no_match(self):
        assert self.metric.compute("hello", "world") == 0.0

    def test_whitespace_handling(self):
        assert self.metric.compute("  hello  ", "hello") == 1.0


class TestContainsMetric:
    def setup_method(self):
        self.metric = ContainsMetric()

    def test_contains(self):
        assert self.metric.compute("The answer is 42.", "42") == 1.0

    def test_not_contains(self):
        assert self.metric.compute("The answer is 42.", "99") == 0.0

    def test_case_insensitive(self):
        assert self.metric.compute("Hello World", "hello") == 1.0


class TestLengthRatioMetric:
    def setup_method(self):
        self.metric = LengthRatioMetric()

    def test_same_length(self):
        assert self.metric.compute("abc", "xyz") == 1.0

    def test_shorter(self):
        assert self.metric.compute("ab", "abcd") == 0.5

    def test_longer_capped(self):
        assert self.metric.compute("abcdef", "ab") == 1.0

    def test_empty_reference(self):
        assert self.metric.compute("abc", "") == 0.0
