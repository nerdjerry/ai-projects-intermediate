"""
Concrete prompt runner using an LLM client.

This module contains ``PromptRunner``, the production implementation of
``IPromptRunner``.  It has exactly two responsibilities:

1. **Render** a prompt template by substituting ``{placeholder}`` tokens with
   actual variable values.
2. **Delegate** the rendered prompt to an ``LLMClient`` for completion.

SOLID principles illustrated
-----------------------------
* **Single Responsibility Principle (SRP)** — ``PromptRunner`` only handles
  template rendering + LLM invocation.  It does *not* evaluate results,
  store prompts, or optimise templates — those concerns live in dedicated
  services.
* **Dependency Inversion Principle (DIP)** — The runner depends on the
  ``LLMClient`` *abstraction* (injected via the constructor), not on a
  concrete implementation like ``OpenAIClient``.  This makes it trivial to
  swap LLM providers or inject a mock in tests.
* **Liskov Substitution Principle (LSP)** — ``PromptRunner`` is a valid
  ``IPromptRunner`` and can be used anywhere the interface is expected.

Constructor Injection
---------------------
The ``LLMClient`` dependency is provided through the constructor — a common
form of **Dependency Injection (DI)**.  This pattern makes dependencies
explicit, simplifies testing, and keeps the class loosely coupled.
"""

from typing import Any

from ..interfaces.llm_client import LLMClient
from ..interfaces.prompt_runner import IPromptRunner


class PromptRunner(IPromptRunner):
    """Renders prompt templates and forwards them to an LLM.

    This is the default ``IPromptRunner`` implementation used in production.
    Because the ``LLMClient`` is injected, the runner remains agnostic to the
    underlying model provider.
    """

    def __init__(self, llm_client: LLMClient):
        """Create a ``PromptRunner``.

        Parameters
        ----------
        llm_client : LLMClient
            The LLM provider to use for completions.  Injected as an
            abstraction so any concrete client can be substituted (DIP).
        """
        self._llm = llm_client

    async def run(
        self, prompt_template: str, variables: dict[str, str], **kwargs: Any
    ) -> str:
        """Render *prompt_template* with *variables* and return the LLM's response.

        The rendering uses Python's built-in ``str.format``, so template
        placeholders must match the keys in *variables*.
        """
        # Step 1: Render the template (e.g. "Hello {name}" → "Hello Alice").
        rendered = prompt_template.format(**variables)
        # Step 2: Delegate to the injected LLM client for completion.
        return await self._llm.complete(rendered, **kwargs)
