"""FastAPI route definitions for the RAG Q&A API."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from ..config import Settings
from ..generation.generator import Generator
from ..ingestion.loader import SUPPORTED_EXTENSIONS
from ..ingestion.pipeline import IngestionPipeline
from ..retrieval.retriever import Retriever
from .models import (
    AnswerResponse,
    DocumentInfo,
    DocumentListResponse,
    IngestResponse,
    QuestionRequest,
    RemoveResponse,
    SourceResponse,
    UploadResponse,
)

router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


# --- Q&A ---

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask a question about the ingested documents."""
    settings = _get_settings()
    retriever = Retriever(settings)
    generator = Generator(settings)

    chunks = retriever.retrieve(request.question)
    answer = generator.generate(request.question, chunks)

    return AnswerResponse(
        answer=answer.text,
        sources=[
            SourceResponse(
                document=s.document,
                chunk_index=s.chunk_index,
                passage_number=s.passage_number,
                score=s.score,
            )
            for s in answer.sources
        ],
        is_supported=answer.is_supported,
    )


# --- Document management ---

@router.post("/ingest", response_model=IngestResponse)
def ingest_all():
    """Re-ingest all documents from the documents directory."""
    settings = _get_settings()
    pipeline = IngestionPipeline(settings)
    stats = pipeline.ingest_all()
    return IngestResponse(**stats)


@router.get("/documents", response_model=DocumentListResponse)
def list_documents():
    """List all indexed documents."""
    settings = _get_settings()
    pipeline = IngestionPipeline(settings)
    docs = pipeline.list_documents()
    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in docs]
    )


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile):
    """Upload a document file and ingest it into the vector store."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    settings = _get_settings()

    # Save the uploaded file to the documents directory
    settings.documents_path.mkdir(parents=True, exist_ok=True)
    dest = settings.documents_path / file.filename
    content = await file.read()
    dest.write_bytes(content)

    # Ingest the file
    pipeline = IngestionPipeline(settings)
    stats = pipeline.ingest_file(dest)

    return UploadResponse(
        filename=file.filename,
        chunks=stats["chunks"],
        message=f"Successfully uploaded and indexed '{file.filename}' ({stats['chunks']} chunks).",
    )


@router.delete("/documents/{filename}", response_model=RemoveResponse)
def remove_document(filename: str):
    """Remove a document from the index and delete the file."""
    settings = _get_settings()
    pipeline = IngestionPipeline(settings)

    # Remove from vector store
    stats = pipeline.remove_document(filename)

    # Delete the file if it exists
    file_path = settings.documents_path / filename
    if file_path.exists():
        file_path.unlink()

    return RemoveResponse(
        filename=filename,
        removed_chunks=stats["removed_chunks"],
        message=f"Removed '{filename}' ({stats['removed_chunks']} chunks deleted).",
    )


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
