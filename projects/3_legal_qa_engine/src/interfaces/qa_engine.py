"""
Q&A engine interface — separated from summarization per ISP.

This module defines the **IQAEngine** interface, which is responsible
exclusively for answering questions given a piece of legal context.

**SOLID – Interface Segregation Principle (ISP):**
    "Clients should not be forced to depend on interfaces they do not use."

Rather than having a single monolithic ``ILegalService`` interface that
bundles Q&A, summarization, and risk analysis, the project splits these
concerns into three focused interfaces:
    • ``IQAEngine``      — this module (question answering)
    • ``ISummarizer``     — document summarization
    • ``IRiskAnalyzer``   — contract risk detection

This way, a consumer that only needs Q&A (e.g., a chatbot endpoint)
does not have to carry along summarization or risk analysis methods.

**SOLID – Dependency Inversion Principle (DIP):**
Callers depend on this abstraction, not on the concrete ``QAService``
that lives in ``src/services/inference_service.py``.
"""
from abc import ABC, abstractmethod
from typing import Any


class IQAEngine(ABC):
    """Interface for legal question-answering.

    **ISP in practice:** This interface exposes only one method — ``ask``.
    If a class or endpoint needs only Q&A capabilities, it depends on
    ``IQAEngine`` and nothing else. This keeps coupling minimal.

    **DIP in practice:** The FastAPI routes and Streamlit UI can accept
    any ``IQAEngine`` implementation without knowing its internals.
    """

    @abstractmethod
    async def ask(self, question: str, context: str, **kwargs: Any) -> str:
        """Answer a question given legal context.

        Args:
            question: The user's natural-language question.
            context: The legal text (clause, contract excerpt, etc.)
                     that the answer should be grounded in.
            **kwargs: Additional options for the underlying implementation
                      (e.g., temperature, max_tokens).

        Returns:
            A natural-language answer derived from the context.
        """
        ...
