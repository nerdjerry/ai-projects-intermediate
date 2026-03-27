"""Generator interface — separates data generation from training (ISP)."""
from abc import ABC, abstractmethod
from typing import Any


class IDataGenerator(ABC):
    """Interface for dataset generation."""

    @abstractmethod
    async def generate_dataset(
        self, domain: str, num_samples: int, **kwargs: Any
    ) -> list[dict[str, str]]:
        """Generate Q&A dataset for a given domain."""
        ...
