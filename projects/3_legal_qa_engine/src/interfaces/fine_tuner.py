"""
Fine-tuner interface — swap training backends via LSP.

This module defines the **IFineTuner** interface for model fine-tuning.
It demonstrates two SOLID principles working together:

**SOLID – Liskov Substitution Principle (LSP):**
    "Subtypes must be substitutable for their base types."

Any concrete fine-tuner (OpenAI fine-tune API, Hugging Face Trainer,
LoRA adapter, etc.) can replace another without the caller knowing.
The caller interacts solely through ``start_training`` and
``get_status``, and every subclass must honour those contracts.

**SOLID – Dependency Inversion Principle (DIP):**
High-level orchestration code depends on this interface, not on a
specific training backend. This makes the fine-tuning pipeline
testable (use a mock fine-tuner) and extensible (add new backends).
"""
from abc import ABC, abstractmethod
from typing import Any


class IFineTuner(ABC):
    """Interface for model fine-tuning.

    Concrete implementations wrap a specific training backend
    (e.g., OpenAI fine-tune API, local Hugging Face training loop).

    **LSP guarantee:** Every subclass returns a job ID from
    ``start_training`` and a status dict from ``get_status``.
    Callers can swap implementations freely.
    """

    @abstractmethod
    async def start_training(self, dataset_path: str, **kwargs: Any) -> str:
        """Start a fine-tuning job. Returns job ID.

        Args:
            dataset_path: Path to the JSONL training dataset.
            **kwargs: Backend-specific hyperparameters (epochs, lr, etc.).

        Returns:
            A unique job identifier string that can be used with
            ``get_status`` to poll progress.
        """
        ...

    @abstractmethod
    async def get_status(self, job_id: str) -> dict[str, Any]:
        """Get status of a fine-tuning job.

        Args:
            job_id: The identifier returned by ``start_training``.

        Returns:
            A dict containing at least a ``"status"`` key with values
            like ``"pending"``, ``"running"``, ``"succeeded"``, or
            ``"failed"``.
        """
        ...
