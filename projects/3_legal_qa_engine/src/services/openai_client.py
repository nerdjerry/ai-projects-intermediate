"""OpenAI implementation of the LLM client."""
from typing import Any

from openai import AsyncOpenAI

from ..interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """Concrete LLM client using OpenAI (Liskov-substitutable)."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.0),
        )
        return response.choices[0].message.content or ""
