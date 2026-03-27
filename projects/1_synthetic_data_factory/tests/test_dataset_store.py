"""Tests for the DatasetStore."""
import tempfile

from src.services.dataset_store import DatasetStore


class TestDatasetStore:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.store = DatasetStore(base_dir=self._tmpdir)

    def test_save_and_load(self):
        records = [
            {"question": "What is Python?", "answer": "A programming language."},
        ]
        self.store.save(records, "tech")
        loaded = self.store.load("tech")
        assert len(loaded) == 1
        assert loaded[0]["question"] == "What is Python?"

    def test_load_empty_domain(self):
        result = self.store.load("nonexistent")
        assert result == []

    def test_list_domains(self):
        self.store.save([{"question": "Q1", "answer": "A1"}], "science")
        self.store.save([{"question": "Q2", "answer": "A2"}], "history")
        domains = self.store.list_domains()
        assert set(domains) == {"science", "history"}

    def test_save_appends(self):
        self.store.save([{"question": "Q1", "answer": "A1"}], "domain")
        self.store.save([{"question": "Q2", "answer": "A2"}], "domain")
        loaded = self.store.load("domain")
        assert len(loaded) == 2
