"""FastAPI application entry point."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .routes import router

# Resolve project root: src/rag/api/app.py -> 3 parents up = src/rag, 4 = project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_INDEX_HTML = _PROJECT_ROOT / "static" / "index.html"

app = FastAPI(
    title="RAG Q&A System",
    description="A Retrieval-Augmented Generation system for document Q&A with source attribution.",
    version="0.1.0",
)

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serve the web UI."""
    if _INDEX_HTML.exists():
        return HTMLResponse(content=_INDEX_HTML.read_text(encoding="utf-8"))
    return HTMLResponse(
        content="<h1>Web UI not found</h1><p>Place index.html in the static/ directory.</p>"
    )


if __name__ == "__main__":
    uvicorn.run("rag.api.app:app", host="0.0.0.0", port=8000, reload=False)
