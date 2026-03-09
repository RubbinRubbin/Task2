"""Tests for the document loader."""

import pytest
from pathlib import Path

from rag.ingestion.loader import load_text, load_documents, SUPPORTED_EXTENSIONS, load_document


@pytest.fixture
def tmp_docs(tmp_path):
    """Create temporary test documents."""
    (tmp_path / "test.txt").write_text("Hello world.", encoding="utf-8")
    (tmp_path / "test.md").write_text("# Title\n\nContent here.", encoding="utf-8")
    (tmp_path / "ignored.json").write_text("{}", encoding="utf-8")
    return tmp_path


class TestLoadText:
    def test_load_txt(self, tmp_path):
        f = tmp_path / "sample.txt"
        f.write_text("Sample content.", encoding="utf-8")
        doc = load_text(f)
        assert doc.content == "Sample content."
        assert doc.metadata["source"] == "sample.txt"
        assert doc.metadata["type"] == "txt"

    def test_load_md(self, tmp_path):
        f = tmp_path / "notes.md"
        f.write_text("# Notes\n\nSome notes.", encoding="utf-8")
        doc = load_text(f)
        assert "# Notes" in doc.content
        assert doc.metadata["type"] == "md"


class TestLoadDocuments:
    def test_loads_supported_files(self, tmp_docs):
        docs = load_documents(tmp_docs)
        filenames = {d.metadata["source"] for d in docs}
        assert "test.txt" in filenames
        assert "test.md" in filenames
        assert "ignored.json" not in filenames

    def test_empty_directory(self, tmp_path):
        docs = load_documents(tmp_path)
        assert docs == []

    def test_unsupported_extension_raises(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_document(f)


class TestSupportedExtensions:
    def test_has_required_formats(self):
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
