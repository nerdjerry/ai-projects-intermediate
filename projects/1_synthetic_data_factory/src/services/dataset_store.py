"""Persist generated datasets in Hugging Face-compatible format.

This module handles storage and retrieval of generated Q&A datasets as JSONL
files. Each domain gets its own file, and records are appended to support
incremental generation over time.

Design principles:
  - SRP: This class only handles persistence, not generation or validation.
  - DIP: Could be swapped for a cloud storage implementation via an interface.
"""
import json
import re
from pathlib import Path


# Regex pattern for safe domain/file slugs — prevents path traversal attacks
# by allowing only alphanumeric characters, hyphens, and underscores.
_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_slug(value: str, label: str = "domain") -> str:
    """Validate that a string is a safe filename slug.

    Raises ValueError if the value contains path separators or other
    potentially dangerous characters (e.g. '../' for directory traversal).
    """
    if not value or not _SAFE_SLUG_RE.match(value):
        raise ValueError(
            f"Invalid {label}: {value!r}. "
            f"Only alphanumeric characters, hyphens, and underscores are allowed."
        )
    return value


class DatasetStore:
    """Stores datasets as JSONL files (SRP: persistence only).

    Each domain is stored as a separate `.jsonl` file under `base_dir`.
    Records are appended on save, so multiple generation runs accumulate
    into the same file. This mirrors how Hugging Face datasets use JSONL.
    """

    def __init__(self, base_dir: str = "datasets"):
        """Initialize the store with a base directory for JSONL files."""
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, records: list[dict[str, str]], domain: str) -> str:
        """Save records to a JSONL file and return the file path.

        Args:
            records: List of Q&A dicts with 'question' and 'answer' keys.
            domain: Knowledge domain used as the filename (must be a safe slug).

        Returns:
            Path to the JSONL file where records were written.

        Raises:
            ValueError: If domain contains unsafe characters (path traversal).
        """
        _validate_slug(domain, "domain")
        file_path = self._base / f"{domain}.jsonl"
        with open(file_path, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return str(file_path)

    def load(self, domain: str) -> list[dict[str, str]]:
        """Load records from a domain JSONL file.

        Args:
            domain: Knowledge domain to load (must be a safe slug).

        Returns:
            List of Q&A dicts, or empty list if the domain file doesn't exist.

        Raises:
            ValueError: If domain contains unsafe characters.
        """
        _validate_slug(domain, "domain")
        file_path = self._base / f"{domain}.jsonl"
        if not file_path.exists():
            return []
        records: list[dict[str, str]] = []
        with open(file_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def list_domains(self) -> list[str]:
        """Return available domain names by scanning for JSONL files."""
        return [p.stem for p in self._base.glob("*.jsonl")]
