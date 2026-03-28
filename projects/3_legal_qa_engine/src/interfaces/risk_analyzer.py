"""
Risk analyzer interface — another ISP-compliant slice.

This module defines the **IRiskAnalyzer** interface, whose sole
responsibility is to inspect legal text and return structured risk
findings.

**SOLID – Interface Segregation Principle (ISP):**
Risk analysis is its own interface rather than being bundled with Q&A
or summarization. A microservice that only performs risk scans depends
only on ``IRiskAnalyzer`` and is not burdened by unrelated methods.

**SOLID – Open/Closed Principle (OCP):**
New risk-analysis strategies (e.g., rule-based, ML-based, LLM-based)
can be introduced as new subclasses without changing existing code.
"""
from abc import ABC, abstractmethod
from typing import Any


class IRiskAnalyzer(ABC):
    """Interface for contract risk analysis.

    Implementors must return a list of dictionaries, each describing
    one risk finding with at minimum ``clause``, ``risk_level``, and
    ``explanation`` keys.

    **Design note:** Returning ``list[dict]`` keeps the interface
    generic. A stricter alternative would be a ``RiskFinding`` dataclass,
    but the dict approach allows LLM-generated JSON to pass through
    without an extra mapping step.
    """

    @abstractmethod
    async def analyze_risk(self, text: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Analyze legal text for risks. Returns list of risk findings.

        Args:
            text: Raw legal text to scan for risk indicators.
            **kwargs: Implementation-specific options.

        Returns:
            A list of dicts, each containing at least:
                - ``clause``      : the relevant text excerpt
                - ``risk_level``  : "high", "medium", or "low"
                - ``explanation`` : human-readable reasoning
        """
        ...
