"""Concrete prompt runner using an LLM client."""
from typing import Any

from ..interfaces.llm_client import LLMClient
from ..interfaces.prompt_runner import IPromptRunner


class PromptRunner(IPromptRunner):
    """Renders templates and runs them through an LLM (SRP)."""

    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def run(
        self, prompt_template: str, variables: dict[str, str], **kwargs: Any
    ) -> str:
        rendered = prompt_template.format(**variables)
        return await self._llm.complete(rendered, **kwargs)
