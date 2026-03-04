"""Download the KJB text, chunk by verse, embed, and store in ChromaDB."""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb
import requests
from openai import OpenAI

from kjb_llm import config
from kjb_llm.utils import parse_verses

# Public-domain KJB text hosted on GitHub (one verse per line).
KJB_URL = (
    "https://raw.githubusercontent.com/scrollmapper/bible_databases"
    "/master/txt/KJV/KJV.txt"
)

# Fallback mirror
KJB_URL_FALLBACK = (
    "https://raw.githubusercontent.com/thiagobodruk/bible/master/txt/en_kjv.txt"
)


def _download_kjb(dest: Path) -> Path:
    """Download the KJB plain-text file if not already cached."""
    if dest.exists():
        print(f"Using cached KJB text at {dest}")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)

    for url in (KJB_URL, KJB_URL_FALLBACK):
        print(f"Downloading KJB from {url} ...")
        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            dest.write_text(resp.text, encoding="utf-8")
            print(f"Saved {len(resp.text):,} bytes to {dest}")
            return dest
        except requests.RequestException as exc:
            print(f"  failed ({exc}), trying next source...")

    print("ERROR: Could not download KJB text from any source.", file=sys.stderr)
    sys.exit(1)


def _embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Return embeddings for a batch of texts."""
    resp = client.embeddings.create(input=texts, model=config.EMBEDDING_MODEL)
    return [item.embedding for item in resp.data]


def ingest() -> None:
    """Main ingestion pipeline: download -> parse -> embed -> store."""
    # 1. Download / read the KJB text
    kjb_path = _download_kjb(config.KJB_TEXT_PATH)
    raw = kjb_path.read_text(encoding="utf-8")

    # 2. Parse into verses
    verses = list(parse_verses(raw))
    if not verses:
        print("ERROR: No verses parsed. Check the text format.", file=sys.stderr)
        sys.exit(1)
    print(f"Parsed {len(verses):,} verses.")

    # 3. Set up ChromaDB
    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    chroma = chromadb.PersistentClient(path=str(config.CHROMA_DIR))

    # Delete existing collection if present (re-ingest is idempotent)
    try:
        chroma.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # 4. Embed and upsert in batches
    oai = OpenAI(api_key=config.OPENAI_API_KEY)
    batch_size = 100
    for i in range(0, len(verses), batch_size):
        batch = verses[i : i + batch_size]
        texts = [v["text"] for v in batch]
        ids = [v["reference"] for v in batch]
        metadatas = [
            {"book": v["book"], "chapter": v["chapter"], "verse": v["verse"]}
            for v in batch
        ]
        embeddings = _embed_batch(oai, texts)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        done = min(i + batch_size, len(verses))
        print(f"  embedded {done:,} / {len(verses):,} verses")

    print("Ingestion complete.")


def main() -> None:
    ingest()


if __name__ == "__main__":
    main()
