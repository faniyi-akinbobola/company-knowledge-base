FROM python:3.12-slim

WORKDIR /app

# System deps needed by chromadb, unstructured, sentence-transformers, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files first — better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install all Python dependencies (uv creates .venv inside /app)
RUN uv sync --frozen --no-dev

# Copy the full project (after deps so code changes don't bust the dep cache layer)
COPY . .

# Set PYTHONPATH early so all subsequent RUN steps can import project modules
ENV PYTHONPATH=/app

# Pre-download HuggingFace models so they're baked in (zero cold-start delay)
RUN .venv/bin/python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); print('Models ready.')"

# Build the ChromaDB vector store from raw documents
# No OPENAI_API_KEY needed — ingest only uses local HuggingFace embeddings
RUN .venv/bin/python rag/ingest.py

# HuggingFace Spaces runs as non-root user (UID 1000)
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app \
    && cp -r /root/.cache /home/appuser/.cache 2>/dev/null || true \
    && chown -R appuser:appuser /home/appuser/.cache

USER appuser

# HuggingFace Spaces requires port 7860
EXPOSE 7860

ENV HF_HOME=/home/appuser/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/hub
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Launch Chainlit
CMD ["chainlit", "run", "UI/ui.py", "--host", "0.0.0.0", "--port", "7860", "-h"]
