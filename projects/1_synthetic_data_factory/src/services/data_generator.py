"""Concrete data generator using an LLM client."""
import json
from typing import Any

from ..interfaces.generator import IDataGenerator
from ..interfaces.llm_client import LLMClient

# Domain prompt templates — extend this dict to add new domains (Open/Closed)
DOMAIN_TEMPLATES: dict[str, str] = {
    "science": (
        "Generate a Q&A pair about {domain}. "
        'Return JSON: {{"question": "...", "answer": "..."}}'
    ),
    "history": (
        "Generate a Q&A pair about {domain}. "
        'Return JSON: {{"question": "...", "answer": "..."}}'
    ),
    "technology": (
        "Generate a Q&A pair about {domain}. "
        'Return JSON: {{"question": "...", "answer": "..."}}'
    ),
}

DEFAULT_TEMPLATE = (
    "Generate a Q&A pair about {domain}. "
    'Return JSON: {{"question": "...", "answer": "..."}}'
)


class DataGenerator(IDataGenerator):
    """Generates synthetic Q&A datasets via an LLM (SRP: generation only)."""

    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def generate_dataset(
        self, domain: str, num_samples: int, **kwargs: Any
    ) -> list[dict[str, str]]:
        """Generate *num_samples* Q&A pairs for *domain*."""
        template = DOMAIN_TEMPLATES.get(domain, DEFAULT_TEMPLATE)
        prompts = [template.format(domain=domain) for _ in range(num_samples)]
        raw_responses = await self._llm.generate_batch(prompts, **kwargs)

        records: list[dict[str, str]] = []
        for text in raw_responses:
            try:
                parsed = json.loads(text)
                if "question" in parsed and "answer" in parsed:
                    records.append(
                        {"question": parsed["question"], "answer": parsed["answer"]}
                    )
            except (json.JSONDecodeError, KeyError):
                continue  # skip malformed responses
        return records
