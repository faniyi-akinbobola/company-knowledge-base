import os
from langchain_chroma import Chroma
from embedding import get_embeddings
from chunking import chunk_document


VD_PATH = "data/vector_db"

def create_vectorstore():
    """
    Create a vector store from documents.
    """ 
    vector_store = Chroma.from_documents(
        embedding=get_embeddings(),
        documents=chunk_document("This is a sample document to be chunked and embedded."),
        persist_directory=VD_PATH
    )

    return vector_store


def load_vectorstore():
    """
    Load the existing vector store.
    """

    vector_store = Chroma(
        persist_directory=VD_PATH,
        embedding=get_embeddings()
    )
    return vector_store