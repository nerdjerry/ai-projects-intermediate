"""
Summarizer interface — ISP-compliant, separate from Q&A.

This module defines the **ISummarizer** interface, which is focused
exclusively on condensing legal documents into shorter summaries.

**SOLID – Interface Segregation Principle (ISP):**
    "Clients should not be forced to depend on interfaces they do not use."

Summarization is kept in its own interface so that a component which
only needs summaries (e.g., a document-preview widget) does not have
to depend on the Q&A or risk-analysis interfaces.

Together with ``IQAEngine`` and ``IRiskAnalyzer``, this forms a trio
of focused interfaces that replace what could have been one bloated
``ILegalService`` interface. Each consumer picks only the slice it needs.
"""
from abc import ABC, abstractmethod


class ISummarizer(ABC):
    """Interface for document summarization.

    **ISP in practice:** Only one method — ``summarize`` — is required.
    This makes it trivial to create lightweight mock or stub
    implementations in tests.

    **DIP in practice:** High-level code (routes, UI) depends on this
    abstraction, not on the concrete ``SummarizationService``.
    """

    @abstractmethod
    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Summarize a legal document or clause.

        Args:
            text: The full legal text to be summarized.
            max_length: Suggested maximum character count for the
                        summary. Implementations should honor this
                        as a soft limit.

        Returns:
            A concise summary highlighting key obligations, rights,
            and risk areas.
        """
        ...
