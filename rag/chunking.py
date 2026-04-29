from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_document(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Two-pass markdown-aware chunking.

    Pass 1 — MarkdownHeaderTextSplitter (#, ## and ###):
        Splits on section boundaries at all three header levels.
        strip_headers=False keeps header text in the chunk content so BM25 and
        dense search can match on section names ("Core Values", "Innovation", …).
        Every sub-chunk also gets its parent ## header prepended from metadata
        so BM25 can locate subsections by their parent section name.

    Pass 2 — RecursiveCharacterTextSplitter:
        Sections larger than chunk_size are split further with overlap so no
        context is cut off at a hard boundary.
    """
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    rc_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    all_chunks = []
    for doc in documents:
        try:
            md_chunks = md_splitter.split_text(doc.page_content)
            for md_chunk in md_chunks:
                md_chunk.metadata.update(doc.metadata)

                # Prepend the parent ## section header to every chunk that has one
                # in metadata but not yet in content. This ensures BM25 can match
                # "Core Values" even in ### sub-chunks like "### 1. Innovation".
                h2 = md_chunk.metadata.get("h2")
                if h2 and f"## {h2}" not in md_chunk.page_content:
                    md_chunk.page_content = f"## {h2}\n{md_chunk.page_content}"

                if len(md_chunk.page_content) > chunk_size:
                    sub_chunks = rc_splitter.split_documents([md_chunk])
                    all_chunks.extend(sub_chunks)
                else:
                    all_chunks.append(md_chunk)
        except Exception:
            all_chunks.extend(rc_splitter.split_documents([doc]))

    return all_chunks