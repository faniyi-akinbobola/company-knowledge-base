from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(document, chunk_size: int = 1000, chunk_overlap: int = 200) :
    """
    Split a document into chunks using RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(document)
    return chunks