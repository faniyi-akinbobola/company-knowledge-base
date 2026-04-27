import os
import hashlib
import re
import unicodedata
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, UnstructuredMarkdownLoader, UnstructuredExcelLoader,Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import  OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


DATA_PATH = "data/raw"
VD_PATH = "data/vector_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")



#load the docs
def load_documents(data_path):
    """
    loads all the data documents 
    """

    docs = []

    for file in os.listdir(data_path):
        path = os.path.join(data_path, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".csv"):
            loader = CSVLoader(path)
        elif file.endswith(".md"):
            loader = UnstructuredMarkdownLoader(path)
        elif file.endswith(".xlsx"):
            loader = UnstructuredExcelLoader(path)
        elif file.endswith(".docx"):
            loader = Docx2txtLoader(path)
        else:
            continue

        docs.extend(loader.load())
    
    return docs

def normalize_text(text: str) -> str:
    """
    RAG-friendly normalization
    """

    # Normalize unicode (fix weird characters)
    text = unicodedata.normalize("NFKC", text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix newlines (convert multiple to single)
    text = re.sub(r"\n+", "\n", text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text


def normalize_documents(documents):
    """
    Normalize all loaded documents
    """

    normalized_docs = []

    for doc in documents:

        clean_text = normalize_text(doc.page_content)

        # Get filename or source
        source = doc.metadata.get("source", "unknown")

        # Add context (VERY IMPORTANT)
        enhanced_text = f"{source}:\n{clean_text}"

        normalized_doc = Document(
            page_content=enhanced_text,
            metadata=doc.metadata
        )

        normalized_docs.append(normalized_doc)

    return normalized_docs

#remove duplicates
def remove_duplicates(docs):
    """
    Remove exact duplicate documents using hashing
    """

    seen_hashes = set()
    unique_docs = []

    for doc in docs:

        text = doc.page_content.strip()

        text_hash = hashlib.md5(text.encode()).hexdigest()

        if text_hash not in seen_hashes:
            seen_hashes.add(text_hash)
            unique_docs.append(doc)

    return unique_docs




