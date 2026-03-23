# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KJB-LLM is a Retrieval-Augmented Generation (RAG) system built on the King James Bible. It uses OpenAI embeddings + ChromaDB for verse retrieval and GPT-4o-mini for generating scripturally-grounded answers. The system ships as a FastAPI backend with multi-platform frontends (mobile via Expo, desktop via Electron, web via Expo Web export).

## Build & Test Commands

### Backend (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run a single test file
pytest tests/test_utils.py -v

# Run the API server (requires OPENAI_API_KEY)
python -m kjb_llm.api

# Ingest KJB verses into ChromaDB (first-time setup)
python -m kjb_llm.ingest

# Interactive query CLI
python -m kjb_llm.query
# One-shot: python -m kjb_llm.query "What does the Bible say about love?"
# JSON output: python -m kjb_llm.query --json "question"
```

### Mobile (React Native / Expo)
```bash
cd mobile
npm ci
npm start              # Expo dev server
npm run android        # Android emulator
npm run ios            # iOS simulator
npm run web            # Web browser
npx expo export --platform web   # Static web build (output: mobile/dist/)
```

### Desktop (Electron)
```bash
cd desktop
npm ci
# Desktop loads the Expo web export from desktop/renderer/
npx electron .                    # Dev run
npx electron-builder --linux      # Build Linux (.AppImage, .deb)
npx electron-builder --mac        # Build macOS (.dmg)
npx electron-builder --win        # Build Windows (.exe)
```

### Docker
```bash
docker build -t kjb-llm .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... -v kjb_data:/app/data kjb-llm
```

## Architecture

**Backend (`kjb_llm/`)** — Python package with CLI entry points (`kjb-query`, `kjb-ingest`, `kjb-server` via setup.py):
- `config.py` — Centralized env-var-based settings (models, paths, API host/port, retrieval params)
- `api.py` — FastAPI server with three routes: `POST /ask`, `GET /health`, `GET /stats`
- `query.py` — Core RAG logic: embed question → ChromaDB similarity search (top_k=10) → GPT-4o-mini completion with constrained system prompt. Also serves as CLI.
- `ingest.py` — Downloads KJB text from public sources, parses verses, batch-embeds (chunks of 100) via OpenAI, upserts to ChromaDB (`data/chroma/`)
- `utils.py` — Verse regex parser for "Book Chapter:Verse Text" format

**Mobile (`mobile/`)** — Expo/React Native app (SDK 52, React 18.3):
- `App.js` → `src/HomeScreen.js` — Chat UI with gold (#c9a227) user bubbles on dark navy (#1a1a2e) background
- `src/api.js` — Backend client using `EXPO_PUBLIC_API_URL` env var (default: `http://localhost:8000`)

**Desktop (`desktop/`)** — Electron wrapper that loads the Expo web export from `renderer/`:
- `main.js` — 480×800 window with context isolation enabled
- Build pipeline: Expo web export → copy to `desktop/renderer/` → electron-builder

## Key Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | (required) | OpenAI API authentication |
| `KJB_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `KJB_CHAT_MODEL` | `gpt-4o-mini` | Chat completion model |
| `KJB_TOP_K` | `10` | Verses retrieved per query |
| `KJB_CHROMA_DIR` | `data/chroma` | ChromaDB persistence path |
| `KJB_API_HOST` | `0.0.0.0` | API server bind address |
| `KJB_API_PORT` | `8000` | API server port |
| `EXPO_PUBLIC_API_URL` | `http://localhost:8000` | Mobile/web API endpoint |

## CI/CD & Release

- **CI tests** run on push/PR to `main` (Python 3.11 + 3.12)
- **All build workflows** (Android, iOS, Web, Desktop, Docker) trigger on `v*` tags
- Tag with `v*` to create a release — artifacts auto-attach to the GitHub Release
- Required secrets: `EXPO_TOKEN` (EAS builds), `GITHUB_TOKEN` (automatic)
- Required variable: `API_URL` (production API base, default `https://api.kjbllm.app`)

## Data Directory

The `data/` directory (gitignored) holds:
- `data/kjb.txt` — Downloaded KJB text (cached after first ingest)
- `data/chroma/` — ChromaDB vector store (persistent)
