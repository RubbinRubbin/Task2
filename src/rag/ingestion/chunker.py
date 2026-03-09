"""Recursive text chunker that splits documents into overlapping chunks."""

from dataclasses import dataclass, field

from .loader import Document


@dataclass
class Chunk:
    """A text chunk with metadata linking it back to its source document."""

    text: str
    metadata: dict = field(default_factory=dict)


class RecursiveChunker:
    """Splits text into chunks using a hierarchy of separators.

    Tries splitting on paragraph boundaries first, then lines, then sentences,
    and finally by character count as a last resort. This preserves semantic
    coherence within chunks as much as possible.
    """

    SEPARATORS = ["\n\n", "\n", ". ", " "]

    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be >= 0 and < chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, document: Document) -> list[Chunk]:
        """Split a document into overlapping chunks."""
        text = document.content.strip()
        if not text:
            return []

        pieces = self._recursive_split(text, 0)
        chunks = self._merge_with_overlap(pieces)

        return [
            Chunk(
                text=chunk_text,
                metadata={**document.metadata, "chunk_index": i},
            )
            for i, chunk_text in enumerate(chunks)
        ]

    def _recursive_split(self, text: str, sep_index: int) -> list[str]:
        """Recursively split text using separators from coarsest to finest."""
        if len(text) <= self.chunk_size:
            return [text]

        if sep_index >= len(self.SEPARATORS):
            # Last resort: hard split by character count
            return self._hard_split(text)

        separator = self.SEPARATORS[sep_index]
        parts = text.split(separator)

        if len(parts) == 1:
            # This separator doesn't split the text, try the next one
            return self._recursive_split(text, sep_index + 1)

        result = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if len(part) <= self.chunk_size:
                result.append(part)
            else:
                # Part is still too large, split with finer separator
                result.extend(self._recursive_split(part, sep_index + 1))

        return result

    def _hard_split(self, text: str) -> list[str]:
        """Split text by character count when no separator works."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end
        return chunks

    def _merge_with_overlap(self, pieces: list[str]) -> list[str]:
        """Merge small pieces into chunks of target size with overlap."""
        if not pieces:
            return []

        chunks = []
        current = pieces[0]

        for piece in pieces[1:]:
            combined = current + " " + piece
            if len(combined) <= self.chunk_size:
                current = combined
            else:
                chunks.append(current)
                # Create overlap from the end of the current chunk
                if self.overlap > 0 and len(current) > self.overlap:
                    overlap_text = current[-self.overlap :]
                    # Try to start overlap at a word boundary
                    space_idx = overlap_text.find(" ")
                    if space_idx != -1:
                        overlap_text = overlap_text[space_idx + 1 :]
                    current = overlap_text + " " + piece
                else:
                    current = piece

        if current:
            chunks.append(current)

        return chunks
