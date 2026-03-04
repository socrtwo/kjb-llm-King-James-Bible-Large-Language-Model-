"""FastAPI server that exposes the KJB-LLM query engine as a REST API.

Endpoints
---------
POST /ask        -- {"question": "..."} -> {"answer": ..., "verses": [...]}
GET  /health     -- simple liveness check
GET  /stats      -- verse count in the vector store
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kjb_llm import config
from kjb_llm.query import ask

app = FastAPI(
    title="KJB-LLM API",
    version="0.1.0",
    description="Ask questions in contemporary English, get answers grounded in the King James Bible.",
)

# Allow all origins so the mobile app can reach the server during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / response models ────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str


class VerseItem(BaseModel):
    reference: str
    text: str


class AskResponse(BaseModel):
    answer: str
    verses: list[VerseItem]


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    import chromadb

    try:
        chroma = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        collection = chroma.get_collection(config.COLLECTION_NAME)
        return {"verses": collection.count()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    result = ask(req.question)
    return AskResponse(**result)


def main() -> None:
    uvicorn.run(
        "kjb_llm.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
