"""Prompt runner interface — separates testing from optimization (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class IPromptRunner(ABC):
    """Interface for executing prompt templates."""

    @abstractmethod
    async def run(self, prompt_template: str, variables: dict[str, str], **kwargs: Any) -> str:
        """Render *prompt_template* with *variables* and return the LLM response."""
        ...
