"""Tests for the API models and basic validation."""

import pytest

from rag.api.models import QuestionRequest, AnswerResponse, SourceResponse


class TestQuestionRequest:
    def test_valid_question(self):
        req = QuestionRequest(question="What is Python?")
        assert req.question == "What is Python?"

    def test_empty_question_rejected(self):
        with pytest.raises(Exception):
            QuestionRequest(question="")


class TestAnswerResponse:
    def test_supported_answer(self):
        resp = AnswerResponse(
            answer="Python is a language.",
            sources=[
                SourceResponse(
                    document="test.md",
                    chunk_index=0,
                    passage_number=1,
                    score=0.85,
                )
            ],
            is_supported=True,
        )
        assert resp.is_supported
        assert len(resp.sources) == 1
        assert resp.sources[0].document == "test.md"

    def test_unsupported_answer(self):
        resp = AnswerResponse(
            answer="Cannot answer.",
            sources=[],
            is_supported=False,
        )
        assert not resp.is_supported
        assert resp.sources == []
