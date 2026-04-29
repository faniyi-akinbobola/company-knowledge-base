# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Build: install deps, download models, build vector DB
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps needed by some packages (unstructured, chromadb, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install all Python dependencies
RUN uv sync --frozen --no-dev

# Copy the full project
COPY . .

# Pre-download HuggingFace models into the image so cold starts are instant.
# Models are cached to /root/.cache/huggingface which is copied to final stage.
RUN uv run python -c "\
    from sentence_transformers import SentenceTransformer, CrossEncoder; \
    print('Downloading embedding model...'); \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    print('Downloading cross-encoder model...'); \
    CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); \
    print('Models ready.')"

# Build the vector DB from the raw documents so it's baked into the image.
# No OPENAI_API_KEY needed here — ingest only uses local HuggingFace embeddings.
RUN uv run python rag/ingest.py

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime: lean final image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages and project from builder
COPY --from=builder /app /app
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# HuggingFace Spaces runs as a non-root user (UID 1000)
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app \
    && cp -r /root/.cache /home/appuser/.cache \
    && chown -R appuser:appuser /home/appuser/.cache

USER appuser

# HuggingFace Spaces requires port 7860
EXPOSE 7860

# Tell HuggingFace where the model cache lives for this user
ENV HF_HOME=/home/appuser/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/hub

# Launch Chainlit on the Spaces port
CMD ["python", "-m", "chainlit", "run", "UI/ui.py", "--host", "0.0.0.0", "--port", "7860", "-h"]
