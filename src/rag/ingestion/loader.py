"""Document loading from various file formats (TXT, MD, PDF)."""

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf


@dataclass
class Document:
    """A loaded document with its text content and metadata."""

    content: str
    metadata: dict = field(default_factory=dict)


def load_text(path: Path) -> Document:
    """Load a plain text or markdown file."""
    content = path.read_text(encoding="utf-8")
    return Document(
        content=content,
        metadata={"source": path.name, "type": path.suffix.lstrip(".")},
    )


def load_pdf(path: Path) -> Document:
    """Load a PDF file using pymupdf, extracting text page by page."""
    doc = pymupdf.open(str(path))
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()
    return Document(
        content="\n\n".join(pages),
        metadata={"source": path.name, "type": "pdf"},
    )


# Mapping of file extensions to their loader functions
_LOADERS = {
    ".txt": load_text,
    ".md": load_text,
    ".pdf": load_pdf,
}

SUPPORTED_EXTENSIONS = set(_LOADERS.keys())


def load_document(path: Path) -> Document:
    """Load a single document, dispatching to the appropriate loader."""
    ext = path.suffix.lower()
    loader = _LOADERS.get(ext)
    if loader is None:
        raise ValueError(f"Unsupported file format: {ext}. Supported: {SUPPORTED_EXTENSIONS}")
    return loader(path)


def load_documents(directory: Path) -> list[Document]:
    """Load all supported documents from a directory."""
    documents = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(load_document(path))
    return documents
