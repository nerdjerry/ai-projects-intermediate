"""Tests for the PromptStore."""
import tempfile
from src.services.prompt_store import PromptStore


class TestPromptStore:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.store = PromptStore(base_dir=self._tmpdir)

    def test_save_and_list(self):
        self.store.save("greet", "Hello {name}!", {"exact_match": 0.9})
        versions = self.store.list_versions("greet")
        assert len(versions) == 1
        assert versions[0].version == 1

    def test_version_increments(self):
        self.store.save("greet", "v1", {})
        self.store.save("greet", "v2", {})
        versions = self.store.list_versions("greet")
        assert versions[-1].version == 2

    def test_get_best(self):
        self.store.save("greet", "v1", {"exact_match": 0.5})
        self.store.save("greet", "v2", {"exact_match": 0.9})
        best = self.store.get_best("greet", "exact_match")
        assert best is not None
        assert best.template == "v2"

    def test_get_best_empty(self):
        best = self.store.get_best("nonexistent", "exact_match")
        assert best is None

    def test_list_empty(self):
        versions = self.store.list_versions("nonexistent")
        assert versions == []
