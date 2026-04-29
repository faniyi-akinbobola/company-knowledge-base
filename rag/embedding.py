import os
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Module-level singleton — model loads once and is reused across all calls.
_embeddings_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return the shared HuggingFaceEmbeddings instance, loading it once on first call.
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings_instance