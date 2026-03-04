# ─────────────────────────────────────────────────────────────────────────────
# KJB-LLM API server Docker image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY kjb_llm/ kjb_llm/

# Pre-create data directory (volume mount point)
RUN mkdir -p /app/data

EXPOSE 8000

ENV KJB_DATA_DIR=/app/data \
    KJB_CHROMA_DIR=/app/data/chroma \
    KJB_API_HOST=0.0.0.0 \
    KJB_API_PORT=8000

# Run the API server
CMD ["python", "-m", "kjb_llm.api"]
