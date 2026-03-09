"""Simple startup script. Run with: python run.py"""
import sys
from pathlib import Path

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from rag.api.app import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  RAG Q&A System")
    print("  Web UI -> http://127.0.0.1:8080")
    print("  API Docs -> http://127.0.0.1:8080/docs")
    print("=" * 50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8080)
