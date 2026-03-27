"""Builds fine-tuning datasets from legal documents (SRP)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Clause:
    """A single clause extracted from a contract."""

    text: str
    label: str = ""
    risk_level: str = "low"


class DatasetBuilder:
    """Builds JSONL datasets from legal documents (SRP: dataset construction)."""

    def chunk_text(self, text: str, max_chars: int = 1000) -> list[str]:
        """Split text into chunks at paragraph boundaries."""
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if current_len + len(para) > max_chars and current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(para)
            current_len += len(para)

        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def label_clause(self, text: str) -> Clause:
        """Label a clause with risk level based on keyword heuristics."""
        text_lower = text.lower()
        high_risk_keywords = [
            "indemnify", "indemnification", "liability", "termination",
            "penalty", "liquidated damages", "breach",
        ]
        medium_risk_keywords = [
            "warranty", "limitation", "confidential", "non-compete",
            "arbitration", "jurisdiction",
        ]

        for kw in high_risk_keywords:
            if kw in text_lower:
                return Clause(text=text, label=kw, risk_level="high")
        for kw in medium_risk_keywords:
            if kw in text_lower:
                return Clause(text=text, label=kw, risk_level="medium")
        return Clause(text=text, label="general", risk_level="low")

    def build_qa_pairs(
        self, clauses: list[Clause],
    ) -> list[dict[str, str]]:
        """Generate Q&A training pairs from labeled clauses."""
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
        """Save records to JSONL format."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return str(out)
