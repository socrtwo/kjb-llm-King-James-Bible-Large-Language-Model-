"""Smoke tests for the FastAPI endpoints (no OpenAI key needed)."""

from fastapi.testclient import TestClient

from kjb_llm.api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ask_empty_question():
    resp = client.post("/ask", json={"question": "  "})
    assert resp.status_code == 422
