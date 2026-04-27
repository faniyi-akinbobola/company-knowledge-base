import os
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def get_embeddings():
    """
    Initialize HuggingFaceEmbeddings with the specified model.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return embeddings