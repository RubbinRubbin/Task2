"""Ingestion pipeline: load documents, chunk, embed, and store in ChromaDB."""

from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from ..config import Settings
from .chunker import RecursiveChunker
from .loader import load_document, load_documents


class IngestionPipeline:
    """Orchestrates the full ingestion flow: load → chunk → embed → store."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.chunker = RecursiveChunker(settings.chunk_size, settings.chunk_overlap)

        embedding_fn = OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
        )

        self.client = chromadb.PersistentClient(path=str(settings.chroma_path))
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_all(self, documents_dir: Path | None = None) -> dict:
        """Ingest all documents from the specified directory.

        Returns stats about the ingestion (document count, chunk count).
        """
        directory = documents_dir or self.settings.documents_path
        documents = load_documents(directory)

        if not documents:
            return {"documents": 0, "chunks": 0}

        total_chunks = 0
        for doc in documents:
            chunks = self.chunker.split(doc)
            if not chunks:
                continue

            self.collection.upsert(
                ids=[f"{doc.metadata['source']}_chunk_{c.metadata['chunk_index']}" for c in chunks],
                documents=[c.text for c in chunks],
                metadatas=[c.metadata for c in chunks],
            )
            total_chunks += len(chunks)

        return {"documents": len(documents), "chunks": total_chunks}

    def ingest_file(self, file_path: Path) -> dict:
        """Ingest a single document file.

        Returns stats about the ingestion.
        """
        doc = load_document(file_path)
        chunks = self.chunker.split(doc)

        if not chunks:
            return {"document": file_path.name, "chunks": 0}

        self.collection.upsert(
            ids=[f"{doc.metadata['source']}_chunk_{c.metadata['chunk_index']}" for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )

        return {"document": file_path.name, "chunks": len(chunks)}

    def remove_document(self, filename: str) -> dict:
        """Remove all chunks belonging to a specific document from the vector store."""
        # Query for all chunks from this document
        results = self.collection.get(
            where={"source": filename},
        )

        if not results["ids"]:
            return {"document": filename, "removed_chunks": 0}

        self.collection.delete(ids=results["ids"])
        return {"document": filename, "removed_chunks": len(results["ids"])}

    def list_documents(self) -> list[dict]:
        """List all indexed documents with their chunk counts."""
        all_data = self.collection.get(include=["metadatas"])

        doc_stats: dict[str, dict] = {}
        for meta in all_data["metadatas"]:
            source = meta["source"]
            if source not in doc_stats:
                doc_stats[source] = {
                    "filename": source,
                    "type": meta.get("type", "unknown"),
                    "chunks": 0,
                }
            doc_stats[source]["chunks"] += 1

        return list(doc_stats.values())

    def clear(self) -> None:
        """Remove all documents from the vector store."""
        self.client.delete_collection(self.settings.collection_name)
        embedding_fn = OpenAIEmbeddingFunction(
            api_key=self.settings.openai_api_key,
            model_name=self.settings.embedding_model,
        )
        self.collection = self.client.get_or_create_collection(
            name=self.settings.collection_name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
