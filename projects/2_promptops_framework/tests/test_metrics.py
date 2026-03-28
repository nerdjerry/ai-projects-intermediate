"""
Tests for the built-in metrics.

Each concrete ``IMetric`` subclass shipped with the framework gets its own
test class here.  The tests verify both the "happy path" and important edge
cases (whitespace handling, case sensitivity, division-by-zero guards).

Why test individual metrics?
----------------------------
Although the ``PromptEvaluator`` tests cover end-to-end scoring, testing
each metric in isolation follows the **Single Responsibility Principle (SRP)**
applied to tests: every test class validates exactly one unit of behaviour.
If a metric's logic changes, only the corresponding test class needs updating.

These tests also serve as **living documentation** — a learner can read each
test to understand exactly what a metric does, without looking at the
implementation.

LSP verification
----------------
Because all three metric classes implement the same ``IMetric`` interface
(``name`` property + ``compute`` method), the fact that these tests all pass
implicitly demonstrates the **Liskov Substitution Principle**: any of these
metrics can replace ``IMetric`` wherever it is expected.
"""

from src.services.metrics import ExactMatchMetric, ContainsMetric, LengthRatioMetric


class TestExactMatchMetric:
    """Tests for ``ExactMatchMetric``."""

    def setup_method(self):
        """Create a fresh metric instance before each test."""
        self.metric = ExactMatchMetric()

    def test_exact_match(self):
        """Identical strings should score 1.0."""
        assert self.metric.compute("hello", "hello") == 1.0

    def test_no_match(self):
        """Different strings should score 0.0."""
        assert self.metric.compute("hello", "world") == 0.0

    def test_whitespace_handling(self):
        """Leading/trailing whitespace should be ignored during comparison."""
        assert self.metric.compute("  hello  ", "hello") == 1.0


class TestContainsMetric:
    """Tests for ``ContainsMetric``."""

    def setup_method(self):
        """Create a fresh metric instance before each test."""
        self.metric = ContainsMetric()

    def test_contains(self):
        """Score should be 1.0 when the reference appears in the prediction."""
        assert self.metric.compute("The answer is 42.", "42") == 1.0

    def test_not_contains(self):
        """Score should be 0.0 when the reference is absent from the prediction."""
        assert self.metric.compute("The answer is 42.", "99") == 0.0

    def test_case_insensitive(self):
        """Comparison should be case-insensitive."""
        assert self.metric.compute("Hello World", "hello") == 1.0


class TestLengthRatioMetric:
    """Tests for ``LengthRatioMetric``."""

    def setup_method(self):
        """Create a fresh metric instance before each test."""
        self.metric = LengthRatioMetric()

    def test_same_length(self):
        """Equal-length strings should yield a ratio of 1.0."""
        assert self.metric.compute("abc", "xyz") == 1.0

    def test_shorter(self):
        """A prediction half the length of the reference should score 0.5."""
        assert self.metric.compute("ab", "abcd") == 0.5

    def test_longer_capped(self):
        """A prediction longer than the reference should be capped at 1.0."""
        assert self.metric.compute("abcdef", "ab") == 1.0

    def test_empty_reference(self):
        """An empty reference should return 0.0 (avoid division by zero)."""
        assert self.metric.compute("abc", "") == 0.0
