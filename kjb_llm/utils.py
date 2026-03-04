"""Shared helpers for KJB-LLM."""

from __future__ import annotations

import re
from typing import Iterator

# ── KJB verse parser ─────────────────────────────────────────────────────────
# Handles lines like:
#   Genesis 1:1  In the beginning God created the heaven and the earth.
#   1 Samuel 3:10  And the LORD came, and stood, and called as at other times...
_VERSE_RE = re.compile(
    r"^(\d?\s*[A-Z][a-zA-Z]+(?:\s+[a-zA-Z]+)*)\s+(\d+):(\d+)\s+(.*)",
)


def parse_verses(text: str) -> Iterator[dict]:
    """Yield dicts with keys: book, chapter, verse, text, reference."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _VERSE_RE.match(line)
        if m:
            book = m.group(1).strip()
            chapter = m.group(2)
            verse = m.group(3)
            body = m.group(4).strip()
            yield {
                "book": book,
                "chapter": int(chapter),
                "verse": int(verse),
                "text": body,
                "reference": f"{book} {chapter}:{verse}",
            }
