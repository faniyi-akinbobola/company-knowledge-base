import csv
import os
import hashlib
import re
import unicodedata
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from rag.chunking import chunk_document
from rag.vectorstore import create_vectorstore


DATA_PATH = "data/raw"


def _load_csv_as_docs(path: str) -> list[Document]:
    """
    Convert each row of a CSV file into a human-readable Document.
    Each row becomes: "Field: Value | Field: Value | ..."
    so the text is naturally searchable by field name and value.
    """
    docs = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Build a readable sentence from all columns
            text = " | ".join(
                f"{k.strip()}: {v.strip()}" for k, v in row.items() if v and v.strip()
            )
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": path, "row": i},
                )
            )
    return docs


def load_documents(data_path):
    """
    Load all .md and .csv files from data_path.
    - .md  files: loaded as raw text so the markdown-aware chunker
                  can split on section headers.
    - .csv files: each row is converted to a readable key:value
                  Document so employee/benefits data is searchable.
    """
    docs = []
    for file in sorted(os.listdir(data_path)):
        path = os.path.join(data_path, file)
        if file.endswith(".md"):
            loader = TextLoader(path, encoding="utf-8")
            docs.extend(loader.load())
        elif file.endswith(".csv"):
            docs.extend(_load_csv_as_docs(path))
    return docs


def normalize_text(text: str) -> str:
    """
    Light normalization that preserves markdown structure.
    Only collapses excess blank lines and trims per-line whitespace.
    Does NOT collapse newlines into spaces (that destroys headers).
    """
    # Fix unicode characters
    text = unicodedata.normalize("NFKC", text)
    # Collapse 3+ consecutive blank lines into two (single blank line)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces/tabs within a line (but NOT newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # Strip leading/trailing spaces from each line
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


def normalize_documents(documents):
    """
    Normalize all loaded documents, preserving markdown structure.
    """
    normalized_docs = []
    for doc in documents:
        clean_text = normalize_text(doc.page_content)
        normalized_doc = Document(
            page_content=clean_text,
            metadata=doc.metadata,
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


def ingest():
    print("loading all the docs from the raw folder")
    docs = load_documents(DATA_PATH)
    print(f"loaded {len(docs)} documents")

    print("Normalizing the docs")
    docs = normalize_documents(documents=docs)

    print("removing exact duplicate content")
    refined_docs = remove_duplicates(docs=docs)
    print(f"finished deduplication. {len(refined_docs)} unique documents ready for vectorization")

    print("Chunking and creating vector store...")
    create_vectorstore(refined_docs)  # ✅ Chunks + embeds + persists

if __name__ == "__main__":
    ingest()