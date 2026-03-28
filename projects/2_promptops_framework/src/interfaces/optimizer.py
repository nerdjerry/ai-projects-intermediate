"""
Optimizer interface — separate from testing (ISP).

This module declares the ``IOptimizer`` abstraction: a contract for any
service that can automatically *improve* a prompt template given a set of
few-shot examples.

Why a dedicated interface?
--------------------------
Optimization and evaluation are conceptually different concerns.  Bundling
them into a single "PromptService" would violate two SOLID principles:

* **Single Responsibility Principle (SRP)** — one class would have two
  independent reasons to change (evaluation logic *and* optimization logic).
* **Interface Segregation Principle (ISP)** — consumers that only need to
  *evaluate* prompts would be forced to depend on optimization methods they
  never call, and vice-versa.

By splitting optimization into its own interface the codebase stays modular:
a new optimization strategy (e.g. genetic search, DSPy-style compilation)
can be plugged in without affecting evaluation or prompt running.

The interface is ``async`` because optimization typically requires one or more
LLM calls — keeping it asynchronous avoids blocking the event loop.
"""

from abc import ABC, abstractmethod
from typing import Any


class IOptimizer(ABC):
    """Abstract interface for prompt-template optimization.

    Implementations receive a prompt template and a list of input/output
    examples, then return a *refined* version of the template that is
    expected to produce better outputs.

    Depending only on this abstraction (rather than a concrete optimizer)
    follows the **Dependency Inversion Principle (DIP)**.
    """

    @abstractmethod
    async def optimize(
        self, prompt_template: str, examples: list[dict[str, str]], **kwargs: Any
    ) -> str:
        """Return an improved version of *prompt_template*.

        Parameters
        ----------
        prompt_template : str
            The current prompt template containing ``{variable}`` placeholders.
        examples : list[dict[str, str]]
            Few-shot examples, each mapping variable names to their values.
        **kwargs : Any
            Strategy-specific options (number of iterations, temperature…).

        Returns
        -------
        str
            The optimized prompt template.
        """
        ...
