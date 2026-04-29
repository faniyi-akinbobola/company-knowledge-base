import os
from langchain_chroma import Chroma
from rag.embedding import get_embeddings
from rag.chunking import chunk_document


VD_PATH = "data/vector_db"


def create_vectorstore(docs):
    """
    Chunk and embed documents, then persist to ChromaDB.
    """
    embeddings = get_embeddings()
    chunks = chunk_document(docs, chunk_size=1500, chunk_overlap=300)

    vector_store = Chroma.from_documents(
        embedding=embeddings,
        documents=chunks,
        persist_directory=VD_PATH
    )

    print(f"✅ Vector store created with {len(chunks)} chunks")
    return vector_store


def load_vectorstore():
    """
    Load the existing vector store. Self-contained — no args needed.
    """
    embeddings = get_embeddings()

    vector_store = Chroma(
        persist_directory=VD_PATH,
        embedding_function=embeddings  # ✅ Correct param name
    )
    return vector_store