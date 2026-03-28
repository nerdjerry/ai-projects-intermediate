"""Concrete data generator using an LLM client.

This module sends prompts to an LLM and parses the returned JSON into Q&A
pairs. It follows the Open/Closed Principle: new domains can be added by
extending DOMAIN_TEMPLATES without modifying existing code.

Design principles:
  - SRP: Only responsible for generating data, not validating or storing it.
  - OCP: New domain templates are added to the dictionary, not via code changes.
  - DIP: Depends on the abstract LLMClient, not a concrete provider.
"""
import json
from typing import Any

from ..interfaces.generator import IDataGenerator
from ..interfaces.llm_client import LLMClient

# Domain prompt templates — extend this dict to add new domains (Open/Closed).
# Each template instructs the LLM to return a JSON object with 'question' and
# 'answer' keys. Domain-specific templates can provide richer instructions.
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
    """Generates synthetic Q&A datasets via an LLM (SRP: generation only).

    Uses the injected LLMClient to send prompts and parse JSON responses.
    Malformed or non-dict responses are silently skipped so that partial
    failures don't abort the entire batch.
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize with an abstract LLM client (DIP — any provider works)."""
        self._llm = llm_client

    async def generate_dataset(
        self, domain: str, num_samples: int, **kwargs: Any
    ) -> list[dict[str, str]]:
        """Generate *num_samples* Q&A pairs for *domain*.

        Sends one prompt per sample to the LLM and parses the JSON responses.
        Only responses that are valid JSON objects with 'question' and 'answer'
        keys are kept — everything else is skipped gracefully.
        """
        template = DOMAIN_TEMPLATES.get(domain, DEFAULT_TEMPLATE)
        prompts = [template.format(domain=domain) for _ in range(num_samples)]
        raw_responses = await self._llm.generate_batch(prompts, **kwargs)

        records: list[dict[str, str]] = []
        for text in raw_responses:
            try:
                parsed = json.loads(text)
                # Guard against valid JSON that isn't a dict (e.g. a number,
                # string, or list). Only dicts can have 'question'/'answer' keys.
                if (
                    isinstance(parsed, dict)
                    and "question" in parsed
                    and "answer" in parsed
                ):
                    records.append(
                        {"question": parsed["question"], "answer": parsed["answer"]}
                    )
            except (json.JSONDecodeError, TypeError):
                continue  # skip malformed or unparseable responses
        return records
