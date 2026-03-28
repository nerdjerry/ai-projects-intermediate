"""
Abstract interface for a Retrieval-Augmented Generation (RAG) query engine.

A query engine sits at the top of the RAG stack: it accepts a natural-language
question, retrieves relevant transcript chunks from the index, and synthesizes
a human-readable answer.

Design Principles:
    - Interface Segregation Principle (ISP): This interface is deliberately
      separated from ``IIndexer`` and ``IRetriever`` so that the answering
      logic is independent of how documents are stored or fetched.  A query
      engine may *use* a retriever internally but should not *be* one.
    - Dependency Inversion Principle (DIP): Callers (API routes, CLI tools)
      depend on ``IQueryEngine`` rather than on a specific LLM provider or
      retrieval strategy.
    - Single Responsibility Principle (SRP): This interface's sole concern
      is answering questions — indexing, retrieval, and transcription belong
      elsewhere.
"""

from abc import ABC, abstractmethod
from typing import Any


class IQueryEngine(ABC):
    """Contract for RAG-based question-answering over meeting transcripts.

    Implementations will typically compose a retriever with a language model
    to generate grounded answers.
    """

    @abstractmethod
    async def query(self, question: str, **kwargs: Any) -> str:
        """Answer a natural-language question using indexed transcripts.

        Args:
            question: The user's question in plain language.
            **kwargs: Implementation-specific options (e.g., ``top_k``,
                ``temperature``).

        Returns:
            A synthesized answer string, ideally citing relevant transcript
            segments.
        """
        ...
