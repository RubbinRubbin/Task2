"""Tests for the recursive text chunker."""

import pytest

from rag.ingestion.chunker import RecursiveChunker, Chunk
from rag.ingestion.loader import Document


@pytest.fixture
def chunker():
    return RecursiveChunker(chunk_size=100, overlap=20)


@pytest.fixture
def small_chunker():
    return RecursiveChunker(chunk_size=50, overlap=10)


def make_doc(text: str, source: str = "test.txt") -> Document:
    return Document(content=text, metadata={"source": source, "type": "txt"})


class TestRecursiveChunkerInit:
    def test_valid_init(self):
        c = RecursiveChunker(chunk_size=256, overlap=32)
        assert c.chunk_size == 256
        assert c.overlap == 32

    def test_invalid_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            RecursiveChunker(chunk_size=0)

    def test_invalid_overlap(self):
        with pytest.raises(ValueError, match="overlap must be"):
            RecursiveChunker(chunk_size=100, overlap=100)

    def test_negative_overlap(self):
        with pytest.raises(ValueError, match="overlap must be"):
            RecursiveChunker(chunk_size=100, overlap=-1)


class TestRecursiveChunkerSplit:
    def test_empty_document(self, chunker):
        doc = make_doc("")
        assert chunker.split(doc) == []

    def test_whitespace_only(self, chunker):
        doc = make_doc("   \n\n  ")
        assert chunker.split(doc) == []

    def test_short_text_single_chunk(self, chunker):
        doc = make_doc("Short text.")
        chunks = chunker.split(doc)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."
        assert chunks[0].metadata["source"] == "test.txt"
        assert chunks[0].metadata["chunk_index"] == 0

    def test_paragraph_splitting(self, small_chunker):
        text = "First paragraph with enough text to exceed the chunk size limit here.\n\nSecond paragraph also with sufficient content to go beyond the limit."
        doc = make_doc(text)
        chunks = small_chunker.split(doc)
        assert len(chunks) >= 2
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_chunk_indices_are_sequential(self, chunker):
        text = "A " * 200  # Long text
        doc = make_doc(text)
        chunks = chunker.split(doc)
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == i

    def test_metadata_preserved(self, chunker):
        doc = make_doc("Some text.", source="notes.md")
        doc.metadata["type"] = "md"
        chunks = chunker.split(doc)
        assert chunks[0].metadata["source"] == "notes.md"
        assert chunks[0].metadata["type"] == "md"

    def test_long_text_multiple_chunks(self, small_chunker):
        text = "Word " * 100
        doc = make_doc(text)
        chunks = small_chunker.split(doc)
        assert len(chunks) > 1
        # Each chunk should not exceed chunk_size by much
        # (overlap merging can create slightly larger chunks)
        for chunk in chunks:
            assert len(chunk.text) <= small_chunker.chunk_size * 1.5

    def test_sentence_splitting(self, small_chunker):
        # Text with no paragraph breaks but sentence boundaries
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        doc = make_doc(text)
        chunks = small_chunker.split(doc)
        assert len(chunks) >= 1
        # All original text should be covered
        combined = " ".join(c.text for c in chunks)
        assert "First sentence" in combined
        assert "Fourth sentence" in combined
