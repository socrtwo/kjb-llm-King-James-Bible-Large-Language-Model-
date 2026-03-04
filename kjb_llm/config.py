"""Centralised configuration for KJB-LLM."""

from __future__ import annotations

import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("KJB_DATA_DIR", PROJECT_ROOT / "data"))
CHROMA_DIR = Path(os.environ.get("KJB_CHROMA_DIR", DATA_DIR / "chroma"))
KJB_TEXT_PATH = DATA_DIR / "kjb.txt"

# ── OpenAI ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
EMBEDDING_MODEL: str = os.environ.get("KJB_EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL: str = os.environ.get("KJB_CHAT_MODEL", "gpt-4o-mini")

# ── Retrieval ────────────────────────────────────────────────────────────────
TOP_K: int = int(os.environ.get("KJB_TOP_K", "10"))
COLLECTION_NAME: str = "kjb_verses"

# ── API server ───────────────────────────────────────────────────────────────
API_HOST: str = os.environ.get("KJB_API_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("KJB_API_PORT", "8000"))
