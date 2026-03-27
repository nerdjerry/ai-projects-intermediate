"""
Builds fine-tuning datasets from legal documents.

This module is responsible for **one thing only**: transforming raw
legal text into structured, labeled datasets suitable for fine-tuning
an LLM. This is a textbook example of the **Single Responsibility
Principle (SRP):**

    "A class should have one, and only one, reason to change."

``DatasetBuilder`` changes only when the dataset-construction logic
changes — never because the model, the API, or the evaluation metrics
change. Those concerns live in their own modules.

Workflow:
    1. ``chunk_text``     — split a long document into paragraph-based chunks
    2. ``label_clause``   — apply keyword heuristics to assign risk labels
    3. ``build_qa_pairs`` — generate question/answer training examples
    4. ``save_jsonl``     — persist the dataset in JSONL format
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Clause:
    """A single clause extracted from a contract.

    Uses Python's ``@dataclass`` decorator for concise, boilerplate-free
    value objects. Fields:
        text       — the raw clause text
        label      — the detected keyword category (e.g., "indemnify")
        risk_level — "high", "medium", or "low"
    """

    text: str
    label: str = ""
    risk_level: str = "low"


class DatasetBuilder:
    """Builds JSONL datasets from legal documents.

    **SOLID – Single Responsibility Principle (SRP):**
    This class handles only dataset construction. It does NOT call the
    LLM, evaluate predictions, or serve HTTP responses — each of those
    tasks is handled by its own dedicated class.

    **Design decision:** The builder is stateless — every method takes
    its inputs as arguments and returns outputs. This makes it easy to
    test, parallelise, and reuse without worrying about shared state.
    """

    def chunk_text(self, text: str, max_chars: int = 1000) -> list[str]:
        """Split text into chunks at paragraph boundaries.

        Args:
            text: The full document text, with paragraphs separated by
                  double newlines (``\\n\\n``).
            max_chars: Soft maximum character count per chunk. A chunk
                       may exceed this if a single paragraph is longer
                       than ``max_chars``.

        Returns:
            A list of text chunks, each formed by joining consecutive
            paragraphs until the character budget is exhausted.
        """
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # If adding this paragraph would exceed the budget and we
            # already have content, flush the current chunk first.
            if current_len + len(para) > max_chars and current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(para)
            current_len += len(para)

        # Don't forget the last accumulated chunk.
        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def label_clause(self, text: str) -> Clause:
        """Label a clause with risk level based on keyword heuristics.

        This is a simple rule-based approach: scan the text for known
        legal keywords and assign the first matching risk level.

        Args:
            text: The clause text to classify.

        Returns:
            A ``Clause`` dataclass with the detected label and risk level.

        Note:
            In a production system this heuristic would be replaced (or
            augmented) by a trained classifier, but the keyword approach
            serves as a useful baseline and works without an LLM.
        """
        text_lower = text.lower()
        # Keywords strongly associated with high-risk legal obligations.
        high_risk_keywords = [
            "indemnify", "indemnification", "liability", "termination",
            "penalty", "liquidated damages", "breach",
        ]
        # Keywords associated with moderate-risk provisions.
        medium_risk_keywords = [
            "warranty", "limitation", "confidential", "non-compete",
            "arbitration", "jurisdiction",
        ]

        # Check high-risk keywords first (higher severity takes priority).
        for kw in high_risk_keywords:
            if kw in text_lower:
                return Clause(text=text, label=kw, risk_level="high")
        for kw in medium_risk_keywords:
            if kw in text_lower:
                return Clause(text=text, label=kw, risk_level="medium")
        # Default: no risky keyword found.
        return Clause(text=text, label="general", risk_level="low")

    def build_qa_pairs(
        self, clauses: list[Clause],
    ) -> list[dict[str, str]]:
        """Generate Q&A training pairs from labeled clauses.

        Each clause is turned into one training example consisting of a
        question, the clause text as context, a templated answer, and
        the risk level. The resulting list can be saved as JSONL for
        fine-tuning.

        Args:
            clauses: List of ``Clause`` objects (output of ``label_clause``).

        Returns:
            A list of dicts, each with keys: ``question``, ``context``,
            ``answer``, and ``risk_level``.
        """
        pairs: list[dict[str, str]] = []
        for clause in clauses:
            pairs.append({
                "question": f"What does this clause say about {clause.label}?",
                "context": clause.text,
                "answer": f"This clause addresses {clause.label} (risk: {clause.risk_level}).",
                "risk_level": clause.risk_level,
            })
        return pairs

    def save_jsonl(self, records: list[dict[str, str]], path: str) -> str:
        """Save records to JSONL format.

        JSONL (JSON Lines) is the standard format for fine-tuning datasets
        in most LLM platforms (OpenAI, Hugging Face, etc.). Each line is
        a self-contained JSON object.

        Args:
            records: The list of training examples to persist.
            path: Destination file path (parent dirs created automatically).

        Returns:
            The resolved path as a string (useful for logging/chaining).
        """
        out = Path(path)
        # Ensure the output directory exists (``parents=True`` creates
        # intermediate directories; ``exist_ok=True`` avoids errors if
        # the directory already exists).
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return str(out)
