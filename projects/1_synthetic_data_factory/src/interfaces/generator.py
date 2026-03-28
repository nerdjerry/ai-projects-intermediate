"""Generator interface — separates data generation from training (ISP).

This module declares what it means to "generate a dataset" without dictating
*how* generation happens.  Concrete implementations (``DataGenerator``) supply
the actual logic, while the rest of the system depends only on this contract.

Design principles:
  - ISP (Interface Segregation Principle): Generation and training are
    separate interfaces (``IDataGenerator`` vs ``ITrainer``).  A service
    that only generates data is never forced to implement training methods
    it doesn't need, and vice-versa.
  - DIP (Dependency Inversion Principle): Consumers depend on this
    abstraction, making it easy to swap the generation strategy (e.g. from
    LLM-based to template-based) without touching callers.
  - OCP (Open/Closed Principle): New generation strategies are added as new
    classes that implement this interface — no modification of existing code.
"""
from abc import ABC, abstractmethod
from typing import Any


class IDataGenerator(ABC):
    """Interface for dataset generation.

    Every concrete generator must produce a list of Q&A dictionaries given
    a knowledge domain and a desired sample count.  The ``**kwargs`` escape
    hatch lets implementations accept extra options (model overrides,
    temperature, etc.) without changing the interface signature.
    """

    @abstractmethod
    async def generate_dataset(
        self, domain: str, num_samples: int, **kwargs: Any
    ) -> list[dict[str, str]]:
        """Generate *num_samples* Q&A pairs for the specified *domain*.

        Args:
            domain: The knowledge domain (e.g. "science", "history").
            num_samples: How many Q&A pairs to produce.
            **kwargs: Implementation-specific options.

        Returns:
            A list of dictionaries, each containing at least ``question``
            and ``answer`` keys.
        """
        ...
