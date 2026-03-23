import os
import hashlib
import re
import unicodedata
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, UnstructuredMarkdownLoader, UnstructuredExcelLoader,Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import  OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
# from langchain.schema import Document


load_dotenv()

DATA_PATH = "data/raw"
VD_PATH = "data/vector_db"
EMBEDDING_MODEL = "text-embedding-3-large"

if(not os.getenv("OPENAI_API_KEY")):
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")


#load the docs
def load_documents(data_path):
    """
    loads all the data documents 
    """

    docs = []

    for file in os.listdir(data_path):
        path = os.path.join(data_path, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(file)
        elif file.endswith(".csv"):
            loader = CSVLoader(file)
        elif file.endswith(".md"):
            loader = UnstructuredMarkdownLoader(file)
        elif file.endswith(".xlsx"):
            loader = UnstructuredExcelLoader(file)
        elif file.endswith(".docx"):
            loader = Docx2txtLoader(file)
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


#split the docs into chunks

def chunk_docs(docs):
    """
    split docs into smaller chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(chunkSize=1000, chunkOverlap=200)
    chunks = text_splitter.create_documents(docs)

    return chunks


def create_vector_store(chunks):
    """
    Create a Chroma vector store from document chunks and persist it.
    """
    #create embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=3072)


    #create vector store
    vector_store = Chroma.from_documents(
        embedding=embeddings,
        documents=chunks,
        persist_directory=VD_PATH
    )

    return vector_store


def ingest():
    print("loading all the docs from the raw folder")
    docs = load_documents(DATA_PATH)
    print(f"loaded {len(docs)} documents")

    print("Normalizing the docs")
    docs = normalize_documents(documents=docs)

    print("removing exact duplicate content")
    refined_docs = remove_duplicates(docs=docs)

    print("chunking the refined docs")
    doc_chunks = chunk_docs(refined_docs)
    print(f"documents have been chunked into {len(doc_chunks)}")

    print("creating vector store")
    vector_store = vector_store(doc_chunks)


if __name__  == "":
    ingest()