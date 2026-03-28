"""Trainer interface — separates training from generation (ISP).

This module declares the contract for model training and evaluation.  It
exists as a *separate* interface from ``IDataGenerator`` so that services
which only generate data are never burdened with training methods they
don't use.

Design principles:
  - ISP (Interface Segregation Principle): Training and generation are
    independent concerns.  By splitting them into ``ITrainer`` and
    ``IDataGenerator``, each concrete class implements only the slice of
    functionality it actually provides.
  - OCP (Open/Closed Principle): New training strategies (LoRA fine-tuning,
    full fine-tuning, distillation) can be added as new classes without
    modifying existing implementations.
  - DIP (Dependency Inversion Principle): Orchestrators that kick off
    training depend on this abstraction, not on a specific ML framework.
"""
from abc import ABC, abstractmethod
from typing import Any


class ITrainer(ABC):
    """Interface for model training and evaluation.

    Concrete implementations wrap a specific ML framework or fine-tuning
    API (e.g. OpenAI fine-tuning, Hugging Face Trainer).  The ``**kwargs``
    parameters let each implementation accept framework-specific options
    without polluting the shared interface.
    """

    @abstractmethod
    async def train(self, dataset_path: str, **kwargs: Any) -> dict[str, Any]:
        """Train or fine-tune a model on the dataset at *dataset_path*.

        Args:
            dataset_path: Filesystem path to the training dataset (JSONL).
            **kwargs: Framework-specific hyperparameters and options.

        Returns:
            A dictionary of training metadata (model path, metrics, etc.).
        """
        ...

    @abstractmethod
    async def evaluate(self, model_path: str, test_data_path: str) -> dict[str, float]:
        """Evaluate a trained model against a held-out test set.

        Args:
            model_path: Path or identifier of the trained model.
            test_data_path: Filesystem path to the test dataset.

        Returns:
            A dictionary mapping metric names to their float values.
        """
        ...
