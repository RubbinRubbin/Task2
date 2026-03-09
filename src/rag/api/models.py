"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")


class SourceResponse(BaseModel):
    document: str
    chunk_index: int
    passage_number: int
    score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    is_supported: bool


class IngestResponse(BaseModel):
    documents: int
    chunks: int


class DocumentInfo(BaseModel):
    filename: str
    type: str
    chunks: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class RemoveResponse(BaseModel):
    filename: str
    removed_chunks: int
    message: str


class ErrorResponse(BaseModel):
    error: str
