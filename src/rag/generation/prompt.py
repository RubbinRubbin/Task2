"""Prompt templates for RAG generation."""

from ..retrieval.retriever import RetrievedChunk

QA_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided context.

Rules:
1. Answer the question using ONLY the information in the context below.
2. If the context does not contain enough information to answer the question, respond with:
   "I cannot answer this question based on the available documents."
3. Be concise and precise in your answer.
4. After your answer, list the sources you used in this format:
   Sources:
   - [document_name] (Passage N)"""

QA_USER_TEMPLATE = """Context:
{context}

Question: {question}"""


def format_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a numbered context string for the prompt."""
    passages = []
    for i, chunk in enumerate(chunks, 1):
        passages.append(
            f"[Passage {i} | Source: {chunk.source}]\n{chunk.text}"
        )
    return "\n\n".join(passages)


def build_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """Build the chat messages list for the OpenAI API call."""
    context = format_context(chunks)
    return [
        {"role": "system", "content": QA_SYSTEM_PROMPT},
        {"role": "user", "content": QA_USER_TEMPLATE.format(context=context, question=question)},
    ]
