from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    chroma_persist_dir: str = "data/chroma"
    collection_name: str = "documents"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    temperature: float = 0.1
    documents_dir: str = "documents"
    relevance_threshold: float = 0.3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def documents_path(self) -> Path:
        return Path(self.documents_dir)

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_dir)
