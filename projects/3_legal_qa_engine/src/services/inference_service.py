"""Inference service — implements summarizer, Q&A, and risk analysis."""
from typing import Any

from ..interfaces.llm_client import LLMClient
from ..interfaces.qa_engine import IQAEngine
from ..interfaces.risk_analyzer import IRiskAnalyzer
from ..interfaces.summarizer import ISummarizer


class SummarizationService(ISummarizer):
    """Summarizes legal documents using an LLM (SRP)."""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def summarize(self, text: str, max_length: int = 500) -> str:
        prompt = (
            f"Summarize the following legal text in at most {max_length} characters. "
            f"Focus on key obligations and rights.\n\n{text}"
        )
        return await self._llm.complete(prompt)


class QAService(IQAEngine):
    """Answers legal questions using an LLM (SRP)."""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def ask(self, question: str, context: str, **kwargs: Any) -> str:
        prompt = (
            "You are a legal assistant. Answer the question based on the context.\n\n"
            f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        )
        return await self._llm.complete(prompt)


class RiskAnalysisService(IRiskAnalyzer):
    """Detects risks in legal text using an LLM (SRP)."""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def analyze_risk(self, text: str, **kwargs: Any) -> list[dict[str, Any]]:
        prompt = (
            "Analyze the following legal text for risks. "
            "Return a JSON array of objects with 'clause', 'risk_level' (high/medium/low), "
            "and 'explanation' fields.\n\n" + text
        )
        import json
        response = await self._llm.complete(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"clause": text[:100], "risk_level": "unknown", "explanation": response}]
