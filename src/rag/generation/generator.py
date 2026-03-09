"""Answer generation using an LLM with RAG context."""

from dataclasses import dataclass, field

import openai

from ..config import Settings
from ..retrieval.retriever import RetrievedChunk
from .prompt import build_messages


# Phrases that indicate the LLM could not answer from the context
_UNSUPPORTED_PHRASES = [
    "cannot answer this question",
    "not enough information",
    "no information in the context",
    "does not contain",
    "not mentioned in",
    "no relevant information",
]


@dataclass
class Source:
    """A source reference for an answer."""

    document: str
    chunk_index: int
    passage_number: int
    score: float


@dataclass
class Answer:
    """A generated answer with source attribution and support flag."""

    text: str
    sources: list[Source] = field(default_factory=list)
    is_supported: bool = True


class Generator:
    """Generates answers from retrieved context using an LLM."""

    def __init__(self, settings: Settings):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.temperature

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> Answer:
        """Generate an answer for the question using the retrieved chunks as context.

        If no relevant chunks are provided, returns an unsupported answer
        without calling the LLM.
        """
        if not chunks:
            return Answer(
                text="I cannot answer this question based on the available documents. "
                     "No relevant passages were found.",
                sources=[],
                is_supported=False,
            )

        messages = build_messages(question, chunks)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        answer_text = response.choices[0].message.content

        sources = [
            Source(
                document=chunk.source,
                chunk_index=chunk.chunk_index,
                passage_number=i,
                score=round(chunk.score, 3),
            )
            for i, chunk in enumerate(chunks, 1)
        ]

        is_supported = not self._is_unsupported(answer_text)

        return Answer(
            text=answer_text,
            sources=sources if is_supported else [],
            is_supported=is_supported,
        )

    @staticmethod
    def _is_unsupported(text: str) -> bool:
        """Check if the LLM's response indicates it cannot answer from context."""
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in _UNSUPPORTED_PHRASES)
