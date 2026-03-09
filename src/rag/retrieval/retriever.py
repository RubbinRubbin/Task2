"""Retrieval module: semantic search over the vector store."""

from dataclasses import dataclass

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from ..config import Settings


@dataclass
class RetrievedChunk:
    """A chunk retrieved from the vector store with relevance score."""

    text: str
    source: str
    chunk_index: int
    score: float  # cosine similarity (0 to 1, higher is better)


class Retriever:
    """Retrieves the most relevant chunks for a given query."""

    def __init__(self, settings: Settings):
        self.settings = settings

        embedding_fn = OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
        )

        client = chromadb.PersistentClient(path=str(settings.chroma_path))
        self.collection = client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Retrieve the top-k most relevant chunks for the query.

        Returns chunks sorted by relevance (highest score first).
        Returns an empty list if no chunks meet the relevance threshold.
        """
        k = top_k or self.settings.top_k

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []

        if not results["documents"] or not results["documents"][0]:
            return []

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1 - dist  # cosine distance → cosine similarity
            if score < self.settings.relevance_threshold:
                continue
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    source=meta["source"],
                    chunk_index=meta["chunk_index"],
                    score=score,
                )
            )

        return chunks
