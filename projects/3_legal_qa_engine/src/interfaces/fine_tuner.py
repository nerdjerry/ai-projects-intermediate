"""Fine-tuner interface (LSP — swap backends)."""
from abc import ABC, abstractmethod
from typing import Any


class IFineTuner(ABC):
    """Interface for model fine-tuning."""

    @abstractmethod
    async def start_training(self, dataset_path: str, **kwargs: Any) -> str:
        """Start a fine-tuning job. Returns job ID."""
        ...

    @abstractmethod
    async def get_status(self, job_id: str) -> dict[str, Any]:
        """Get status of a fine-tuning job."""
        ...
