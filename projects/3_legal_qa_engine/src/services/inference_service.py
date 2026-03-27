"""
Inference service — concrete implementations of summarizer, Q&A, and risk analysis.

This is where the abstract interfaces defined in ``src/interfaces/`` are
brought to life. Each service class:

1. Implements exactly **one** interface (ISP).
2. Receives its ``LLMClient`` dependency through the constructor (DIP).
3. Has a single, well-defined responsibility (SRP).

**SOLID principles in action here:**

• **Single Responsibility Principle (SRP):** Each class does one thing:
  ``SummarizationService`` summarizes, ``QAService`` answers questions,
  ``RiskAnalysisService`` detects risks.

• **Dependency Inversion Principle (DIP):** Every class depends on the
  ``LLMClient`` abstraction, not on ``OpenAIClient`` directly. This
  means you can inject a mock client in tests or swap to a different
  provider in production.

• **Liskov Substitution Principle (LSP):** Each class can be used
  wherever its interface is expected (e.g., ``SummarizationService``
  is a valid ``ISummarizer``). Callers never need to know the concrete
  type.

• **Open/Closed Principle (OCP):** Need a different summarization
  strategy? Create a new class implementing ``ISummarizer`` — no
  existing code needs to change.

Design pattern: **Strategy Pattern** — the LLM client is the strategy
object injected into each service, allowing the algorithm (prompt +
model call) to vary independently of the service consumers.
"""
from typing import Any

from ..interfaces.llm_client import LLMClient
from ..interfaces.qa_engine import IQAEngine
from ..interfaces.risk_analyzer import IRiskAnalyzer
from ..interfaces.summarizer import ISummarizer


class SummarizationService(ISummarizer):
    """Summarizes legal documents using an LLM.

    **SRP:** This class is only responsible for summarization.
    **DIP:** It depends on the ``LLMClient`` abstraction, not a concrete SDK.
    """

    def __init__(self, llm: LLMClient):
        # Store the injected LLM client (DIP — depend on abstraction).
        self._llm = llm

    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Summarize legal text by delegating to the injected LLM.

        The prompt engineering here instructs the model to focus on
        key obligations and rights — the most important elements in
        legal documents.

        Args:
            text: The legal text to summarize.
            max_length: Soft character limit for the summary.

        Returns:
            A condensed summary from the LLM.
        """
        prompt = (
            f"Summarize the following legal text in at most {max_length} characters. "
            f"Focus on key obligations and rights.\n\n{text}"
        )
        return await self._llm.complete(prompt)


class QAService(IQAEngine):
    """Answers legal questions using an LLM.

    **SRP:** Handles only question-answering, nothing else.
    **DIP:** Receives the LLM through constructor injection.
    """

    def __init__(self, llm: LLMClient):
        # Store the injected LLM client (DIP — depend on abstraction).
        self._llm = llm

    async def ask(self, question: str, context: str, **kwargs: Any) -> str:
        """Answer a legal question grounded in the provided context.

        The system prompt sets the role ("legal assistant") and
        instructs the model to restrict its answer to the given
        context, reducing hallucination.

        Args:
            question: The user's question in natural language.
            context: The legal text to base the answer on.
            **kwargs: Additional LLM options (forwarded to ``complete``).

        Returns:
            The model's answer as a string.
        """
        prompt = (
            "You are a legal assistant. Answer the question based on the context.\n\n"
            f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        )
        return await self._llm.complete(prompt)


class RiskAnalysisService(IRiskAnalyzer):
    """Detects risks in legal text using an LLM.

    **SRP:** Focused solely on risk detection.
    **DIP:** LLM provider is injected, not hard-coded.

    **Design note:** The prompt asks the LLM to return structured JSON.
    If the LLM's response is not valid JSON (which can happen with
    creative models), a fallback dict is returned to ensure the caller
    always gets a usable result.
    """

    def __init__(self, llm: LLMClient):
        # Store the injected LLM client (DIP — depend on abstraction).
        self._llm = llm

    async def analyze_risk(self, text: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Analyze legal text for risks by prompting the LLM.

        Args:
            text: The legal text to scan for risks.
            **kwargs: Additional LLM options.

        Returns:
            A list of risk-finding dicts with ``clause``,
            ``risk_level``, and ``explanation`` keys.
        """
        prompt = (
            "Analyze the following legal text for risks. "
            "Return a JSON array of objects with 'clause', 'risk_level' (high/medium/low), "
            "and 'explanation' fields.\n\n" + text
        )
        import json
        response = await self._llm.complete(prompt)
        try:
            # Attempt to parse the LLM output as JSON.
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: wrap the raw response so callers still get a
            # list[dict] as promised by the interface contract.
            return [{"clause": text[:100], "risk_level": "unknown", "explanation": response}]
