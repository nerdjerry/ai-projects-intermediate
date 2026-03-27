"""Tests for the DataGenerator with a mock LLM client.

Verifies that the generator correctly parses valid JSON, skips malformed
responses, and handles edge cases like non-dict JSON (numbers, strings, lists).
"""
import json
from typing import Any

import pytest

from src.interfaces.llm_client import LLMClient
from src.services.data_generator import DataGenerator


class FakeLLMClient(LLMClient):
    """Test double that returns canned JSON responses.

    This is a concrete implementation of the abstract LLMClient used only
    in tests (LSP — it can substitute for any LLMClient).
    """

    def __init__(self, responses: list[str]):
        self._responses = responses

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        return self._responses.pop(0) if self._responses else "{}"

    async def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        return [
            self._responses.pop(0) if self._responses else "{}" for _ in prompts
        ]


@pytest.mark.asyncio
class TestDataGenerator:
    async def test_generate_dataset_parses_valid_json(self):
        """Valid Q&A JSON objects should be returned as records."""
        responses = [
            json.dumps(
                {"question": "What is AI?", "answer": "Artificial Intelligence."}
            ),
            json.dumps({"question": "What is ML?", "answer": "Machine Learning."}),
        ]
        gen = DataGenerator(llm_client=FakeLLMClient(responses))
        result = await gen.generate_dataset("tech", num_samples=2)
        assert len(result) == 2

    async def test_generate_dataset_skips_malformed(self):
        """Non-JSON text should be skipped without raising."""
        responses = [
            "not json at all",
            json.dumps({"question": "Good?", "answer": "Yes."}),
        ]
        gen = DataGenerator(llm_client=FakeLLMClient(responses))
        result = await gen.generate_dataset("tech", num_samples=2)
        assert len(result) == 1

    async def test_generate_dataset_empty_responses(self):
        """Empty LLM responses should yield an empty dataset."""
        gen = DataGenerator(llm_client=FakeLLMClient([]))
        result = await gen.generate_dataset("science", num_samples=3)
        assert result == []

    async def test_generate_dataset_skips_non_dict_json(self):
        """Valid JSON that isn't a dict (e.g. number, string, list) should
        be skipped instead of raising a TypeError."""
        responses = [
            "42",                        # valid JSON number
            '"just a string"',           # valid JSON string
            '[1, 2, 3]',                 # valid JSON array
            json.dumps({"question": "Q?", "answer": "A."}),  # valid dict
        ]
        gen = DataGenerator(llm_client=FakeLLMClient(responses))
        result = await gen.generate_dataset("tech", num_samples=4)
        # Only the last response (a dict with question/answer) should be kept
        assert len(result) == 1
        assert result[0]["question"] == "Q?"
