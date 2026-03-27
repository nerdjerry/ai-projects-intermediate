"""Tests for the PromptStore.

Verifies version management, best-by-metric lookup, and security
(path traversal prevention in prompt names).
"""
import tempfile

import pytest

from src.services.prompt_store import PromptStore


class TestPromptStore:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.store = PromptStore(base_dir=self._tmpdir)

    def test_save_and_list(self):
        """Saving a prompt should create version 1."""
        self.store.save("greet", "Hello {name}!", {"exact_match": 0.9})
        versions = self.store.list_versions("greet")
        assert len(versions) == 1
        assert versions[0].version == 1

    def test_version_increments(self):
        """Each save should increment the version number."""
        self.store.save("greet", "v1", {})
        self.store.save("greet", "v2", {})
        versions = self.store.list_versions("greet")
        assert versions[-1].version == 2

    def test_get_best(self):
        """get_best should return the version with the highest metric score."""
        self.store.save("greet", "v1", {"exact_match": 0.5})
        self.store.save("greet", "v2", {"exact_match": 0.9})
        best = self.store.get_best("greet", "exact_match")
        assert best is not None
        assert best.template == "v2"

    def test_get_best_empty(self):
        """get_best on a nonexistent prompt should return None."""
        best = self.store.get_best("nonexistent", "exact_match")
        assert best is None

    def test_list_empty(self):
        """Listing versions for a nonexistent prompt should return []."""
        versions = self.store.list_versions("nonexistent")
        assert versions == []

    def test_path_traversal_rejected_on_save(self):
        """Prompt names with path separators must be rejected to prevent
        writing to arbitrary files outside the store directory."""
        with pytest.raises(ValueError, match="Invalid name"):
            self.store.save("../escape", "template", {})

    def test_path_traversal_rejected_on_list(self):
        """Prompt names with path separators must be rejected on read too."""
        with pytest.raises(ValueError, match="Invalid name"):
            self.store.list_versions("../../etc/passwd")
