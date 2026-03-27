"""Version-controlled prompt storage (SRP: persistence).

This module manages versioned prompt templates stored as JSONL files. Each
prompt name gets its own file, and each save creates a new version. Supports
lookup of all versions and finding the best-scoring version for a given metric.

Design principles:
  - SRP: Only handles persistence and retrieval of prompt versions.
  - OCP: New storage backends can be added by implementing the same interface.

Security:
  - Prompt names are validated against a safe slug pattern to prevent
    path traversal attacks (e.g. '../../etc/passwd').

Concurrency:
  - File locking (fcntl on Unix) prevents race conditions when multiple
    API requests attempt to save versions simultaneously.
"""
from __future__ import annotations

import fcntl
import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


# Safe filename pattern — prevents path traversal by only allowing
# alphanumeric characters, hyphens, and underscores in prompt names.
_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_slug(value: str, label: str = "name") -> str:
    """Validate that a string is a safe filename slug.

    Raises ValueError if the value contains path separators or other
    potentially dangerous characters.
    """
    if not value or not _SAFE_SLUG_RE.match(value):
        raise ValueError(
            f"Invalid {label}: {value!r}. "
            f"Only alphanumeric characters, hyphens, and underscores are allowed."
        )
    return value


@dataclass
class PromptVersion:
    """Immutable snapshot of a prompt template at a specific version.

    Attributes:
        template: The prompt template string (may contain {placeholders}).
        version: Auto-incremented version number (1-based).
        scores: Evaluation scores keyed by metric name (e.g. {'exact_match': 0.9}).
        created_at: Unix timestamp of when this version was created.
    """

    template: str
    version: int
    scores: dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class PromptStore:
    """Stores prompt versions as JSONL files, one file per prompt name.

    Each line in the JSONL file is a serialized PromptVersion. Version numbers
    are auto-incremented using file locking to prevent race conditions.
    """

    def __init__(self, base_dir: str = "prompts"):
        """Initialize the store, creating the base directory if needed."""
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, template: str, scores: dict[str, float] | None = None) -> PromptVersion:
        """Save a new version of a prompt template.

        Uses file locking to safely compute the next version number, even
        under concurrent API requests. The lock is held while reading existing
        versions and appending the new one.

        Args:
            name: Prompt name (must be a safe slug — alphanumeric, hyphens, underscores).
            template: The prompt template string.
            scores: Optional dict of metric scores for this version.

        Returns:
            The newly created PromptVersion with its assigned version number.

        Raises:
            ValueError: If name contains unsafe characters.
        """
        _validate_slug(name)
        path = self._base / f"{name}.jsonl"

        # Use exclusive file locking to prevent race conditions when multiple
        # requests try to save versions concurrently. The lock ensures that
        # version number computation and the append are atomic.
        with open(path, "a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                # Read existing versions to compute the next version number
                fh.seek(0)
                max_version = 0
                for line in fh:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        max_version = max(max_version, data.get("version", 0))

                next_version = max_version + 1
                pv = PromptVersion(template=template, version=next_version, scores=scores or {})
                fh.write(json.dumps(asdict(pv)) + "\n")
                fh.flush()
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

        return pv

    def list_versions(self, name: str) -> list[PromptVersion]:
        """List all saved versions of a prompt.

        Args:
            name: Prompt name (must be a safe slug).

        Returns:
            List of PromptVersion objects in chronological order, or empty
            list if the prompt doesn't exist.

        Raises:
            ValueError: If name contains unsafe characters.
        """
        _validate_slug(name)
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
        """Get the version with the highest score for a given metric.

        Args:
            name: Prompt name (must be a safe slug).
            metric: Name of the metric to rank by (e.g. 'exact_match').

        Returns:
            The best-scoring PromptVersion, or None if no versions exist.

        Raises:
            ValueError: If name contains unsafe characters.
        """
        _validate_slug(name)
        versions = self.list_versions(name)
        if not versions:
            return None
        return max(versions, key=lambda v: v.scores.get(metric, 0.0))
