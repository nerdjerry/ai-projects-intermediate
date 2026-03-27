"""Version-controlled prompt storage (SRP: persistence)."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class PromptVersion:
    """Immutable snapshot of a prompt template."""

    template: str
    version: int
    scores: dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class PromptStore:
    """Stores prompt versions as JSONL."""

    def __init__(self, base_dir: str = "prompts"):
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, template: str, scores: dict[str, float] | None = None) -> PromptVersion:
        versions = self.list_versions(name)
        next_version = max((v.version for v in versions), default=0) + 1
        pv = PromptVersion(template=template, version=next_version, scores=scores or {})
        path = self._base / f"{name}.jsonl"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(pv)) + "\n")
        return pv

    def list_versions(self, name: str) -> list[PromptVersion]:
        path = self._base / f"{name}.jsonl"
        if not path.exists():
            return []
        versions: list[PromptVersion] = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    versions.append(PromptVersion(**data))
        return versions

    def get_best(self, name: str, metric: str) -> PromptVersion | None:
        versions = self.list_versions(name)
        if not versions:
            return None
        return max(versions, key=lambda v: v.scores.get(metric, 0.0))
