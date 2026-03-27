"""OpenAI implementation of the LLM client."""
import asyncio
from typing import Any

from openai import AsyncOpenAI

from ..interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """Concrete LLM client using OpenAI API (Liskov-substitutable)."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI chat completions."""
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content or ""

    async def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate text for multiple prompts concurrently."""
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
