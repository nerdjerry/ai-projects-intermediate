"""Trainer interface — separates training from generation (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class ITrainer(ABC):
    """Interface for model training."""

    @abstractmethod
    async def train(self, dataset_path: str, **kwargs: Any) -> dict[str, Any]:
        """Train/fine-tune a model on the given dataset."""
        ...

    @abstractmethod
    async def evaluate(self, model_path: str, test_data_path: str) -> dict[str, float]:
        """Evaluate a trained model."""
        ...
