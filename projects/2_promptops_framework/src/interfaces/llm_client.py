"""
Abstract LLM client interface.

This module defines the abstract base class (ABC) that every LLM provider must
implement.  It is the cornerstone of the **Dependency Inversion Principle (DIP)**
in this project: high-level services (PromptRunner, optimizers, etc.) depend on
this *abstraction* rather than on any concrete SDK such as OpenAI or Anthropic.

Design decisions
----------------
* **Why an ABC instead of a Protocol?**  ABCs raise ``TypeError`` at
  instantiation time if a subclass forgets to implement ``complete()``, giving
  an immediate, obvious error message — ideal for learners.
* **Why ``async``?**  LLM calls are I/O-bound.  An async interface lets the
  rest of the application stay responsive while waiting for a network response.

SOLID principles illustrated
-----------------------------
* **DIP** — High-level modules depend on this abstraction, not on concrete
  implementations (e.g. ``OpenAIClient``).
* **OCP** — New providers can be added by subclassing ``LLMClient`` without
  modifying existing code.
* **LSP** — Any subclass must honour the contract: accept a prompt string and
  return a completion string, so it can replace ``LLMClient`` transparently.
"""

from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Abstract base class for all LLM providers.

    Every concrete LLM integration (OpenAI, Anthropic, local models, …) must
    inherit from this class and implement the ``complete`` method.

    By programming against this abstraction the rest of the codebase remains
    **decoupled** from any specific vendor SDK — a textbook application of the
    Dependency Inversion Principle (DIP).
    """

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send *prompt* to the language model and return the generated text.

        Parameters
        ----------
        prompt : str
            The fully-rendered prompt string to send to the model.
        **kwargs : Any
            Provider-specific options (model name, temperature, max_tokens …).
            Concrete implementations decide which kwargs they support.

        Returns
        -------
        str
            The model's completion text.
        """
        ...
