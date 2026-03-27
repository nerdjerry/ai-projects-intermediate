"""Persist generated datasets in Hugging Face-compatible format."""
import json
from pathlib import Path


class DatasetStore:
    """Stores datasets as JSONL files (SRP: persistence only)."""

    def __init__(self, base_dir: str = "datasets"):
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, records: list[dict[str, str]], domain: str) -> str:
        """Save records to a JSONL file and return the file path."""
        file_path = self._base / f"{domain}.jsonl"
        with open(file_path, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return str(file_path)

    def load(self, domain: str) -> list[dict[str, str]]:
        """Load records from a domain JSONL file."""
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
        """Return available domain names."""
        return [p.stem for p in self._base.glob("*.jsonl")]
