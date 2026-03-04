# KJB-LLM: King James Bible Language Model

A retrieval-augmented generation (RAG) system trained exclusively on the King James Bible (KJB), designed to answer contemporary language queries with scripturally grounded responses. Delivered as an **Android app** (with iOS, Windows, macOS, Linux, and Web planned).

## Architecture

```
┌──────────────────────────────┐
│   Mobile / Desktop / Web     │  React Native (Expo)
│   Android  (phase 1)         │  iOS, Web, Desktop (planned)
└────────────┬─────────────────┘
             │  REST  /ask
┌────────────▼─────────────────┐
│   Python API  (FastAPI)      │  kjb_llm/api.py
│   ┌────────────────────────┐ │
│   │  Query engine          │ │  kjb_llm/query.py
│   │  ┌──────┐  ┌─────────┐│ │
│   │  │Chroma│  │ OpenAI  ││ │  Embeddings + Chat
│   │  │  DB  │  │ GPT-4o  ││ │
│   │  └──────┘  └─────────┘│ │
│   └────────────────────────┘ │
└──────────────────────────────┘
```

The system uses **OpenAI** models for both embeddings (`text-embedding-3-small`) and answer generation (`gpt-4o-mini`). All answers are grounded exclusively in KJB verse text retrieved from a local ChromaDB vector store.

## Quick start

### 1. Backend (Python)

```bash
# Clone and enter the repo
git clone https://github.com/socrtwo/kjb-llm-King-James-Bible-Large-Language-Model-.git
cd kjb-llm-King-James-Bible-Large-Language-Model-

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Ingest the KJB into the vector store (one-time)
python -m kjb_llm.ingest

# Start the API server
python -m kjb_llm.api
# Server runs at http://localhost:8000
```

### 2. Mobile app (Android-first)

```bash
cd mobile

# Install JS dependencies
npm install

# Start the Expo dev server
npx expo start

# Press 'a' to open on an Android emulator, or scan the QR code
# with Expo Go on a physical device.
```

> **Tip:** On a physical device, set the API URL to your machine's LAN IP:
> `EXPO_PUBLIC_API_URL=http://192.168.x.x:8000 npx expo start`

### 3. Command-line usage

```bash
# Interactive
python -m kjb_llm.query

# One-shot
python -m kjb_llm.query "What does the Bible say about forgiveness?"

# JSON output (for scripting)
python -m kjb_llm.query --json "What is love?"
```

## Project structure

```
kjb-llm-King-James-Bible-Large-Language-Model-/
├── kjb_llm/                   # Python backend
│   ├── __init__.py
│   ├── config.py              # Centralised settings
│   ├── utils.py               # KJB text parsing helpers
│   ├── ingest.py              # Download KJB, embed, store in ChromaDB
│   ├── query.py               # Retrieve verses + generate answer via OpenAI
│   └── api.py                 # FastAPI REST server
├── mobile/                    # React Native (Expo) app
│   ├── App.js                 # Entry point
│   ├── src/
│   │   ├── api.js             # Backend API client
│   │   └── HomeScreen.js      # Main chat UI
│   ├── app.json               # Expo config
│   └── package.json
├── tests/
│   ├── test_utils.py          # Verse parser tests
│   └── test_api.py            # API endpoint smoke tests
├── data/                      # Auto-created at runtime
├── requirements.txt
├── setup.py
├── .gitignore
├── LICENSE
└── README.md
```

## API reference

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/ask` | `{"question": "..."}` | `{"answer": "...", "verses": [{"reference": "...", "text": "..."}]}` |
| `GET` | `/health` | — | `{"status": "ok"}` |
| `GET` | `/stats` | — | `{"verses": 31102}` |

## Configuration

Settings in `kjb_llm/config.py`, overridable via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key |
| `KJB_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `KJB_CHAT_MODEL` | `gpt-4o-mini` | Chat completion model |
| `KJB_TOP_K` | `10` | Verses retrieved per query |
| `KJB_CHROMA_DIR` | `data/chroma` | ChromaDB persistence path |
| `KJB_API_HOST` | `0.0.0.0` | API bind address |
| `KJB_API_PORT` | `8000` | API port |

## Distribution builds (GitHub Actions)

Every platform has a dedicated GitHub Actions workflow under `.github/workflows/`:

| Workflow | File | Trigger | Output |
|----------|------|---------|--------|
| **CI Tests** | `ci-tests.yml` | Push / PR to `main` | pytest results |
| **Android** | `build-android.yml` | Tag `v*` or manual | `.apk` / `.aab` |
| **iOS** | `build-ios.yml` | Tag `v*` or manual | `.ipa` |
| **Web** | `build-web.yml` | Push to `main` or tag | GitHub Pages |
| **Desktop** | `build-desktop.yml` | Tag `v*` or manual | `.AppImage`, `.deb`, `.dmg`, `.exe` |
| **Backend** | `build-backend.yml` | Push to `main` or tag | Docker image (GHCR) |

### Required secrets & variables

| Secret / Variable | Where | Purpose |
|---|---|---|
| `EXPO_TOKEN` | Secret | Expo / EAS authentication |
| `API_URL` | Variable | Production API base URL (default `https://api.kjbllm.app`) |
| `GITHUB_TOKEN` | Automatic | GHCR push, release asset upload |

### Creating a release

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers all build workflows simultaneously. Artifacts are attached to the GitHub Release automatically.

## Distribution roadmap

| Platform | Framework | Status |
|----------|-----------|--------|
| Android | React Native (Expo / EAS) | **Active -- CI/CD ready** |
| iOS | React Native (Expo / EAS) | **Active -- CI/CD ready** |
| Web | Expo Web + GitHub Pages | **Active -- CI/CD ready** |
| Windows | Electron + electron-builder | **Active -- CI/CD ready** |
| macOS | Electron + electron-builder | **Active -- CI/CD ready** |
| Linux | Electron + electron-builder | **Active -- CI/CD ready** |
| Backend | Docker (GHCR) | **Active -- CI/CD ready** |

## Example

```
$ python -m kjb_llm.query "How should I treat my enemies?"

Answer:
  Jesus teaches that you should love your enemies and do good to those
  who hate you. Rather than seeking revenge, you are called to pray for
  those who persecute you and to turn the other cheek.

Supporting verses:
  - Matthew 5:44  "But I say unto you, Love your enemies, bless them
    that curse you, do good to them that hate you..."
  - Luke 6:27  "But I say unto you which hear, Love your enemies, do
    good to them which hate you"
  - Romans 12:20  "Therefore if thine enemy hunger, feed him; if he
    thirst, give him drink..."
```

## License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.

The King James Bible text is in the public domain.
