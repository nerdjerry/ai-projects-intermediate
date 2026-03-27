"""Risk analyzer interface."""
from abc import ABC, abstractmethod
from typing import Any


class IRiskAnalyzer(ABC):
    """Interface for contract risk analysis."""

    @abstractmethod
    async def analyze_risk(self, text: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Analyze legal text for risks. Returns list of risk findings."""
        ...
