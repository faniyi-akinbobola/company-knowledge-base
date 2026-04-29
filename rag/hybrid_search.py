"""
Hybrid Search
=============
Combines dense (Chroma / embedding) and sparse (BM25 / keyword) retrieval,
then fuses the ranked lists using Reciprocal Rank Fusion (RRF).

Why hybrid?
- Dense retrieval excels at semantic similarity ("WFH rules" → remote work policy)
- Sparse retrieval excels at exact keyword matches ("MFA", "FMLA", specific policy names)
- RRF fusion gives the best of both without needing to tune score weights

Architecture:
    query
      ├── dense_retrieve()   → top-k docs by embedding similarity  (Chroma)
      └── sparse_retrieve()  → top-k docs by BM25 keyword score
                ↓
          reciprocal_rank_fusion()
                ↓
          deduplicated, re-ranked list of Documents
"""

from __future__ import annotations

from typing import List
from langchain_core.documents import Document
from rag.vectorstore import load_vectorstore

# BM25 index is built lazily on first call and cached module-level
_bm25_index = None
_bm25_corpus: List[Document] = []

# Cross-encoder reranker — loaded lazily and cached module-level
_cross_encoder = None
_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# ─────────────────────────────────────────────────────────────────────────────
# BM25 index — built once from all docs in the Chroma collection
# ─────────────────────────────────────────────────────────────────────────────

def _build_bm25_index():
    """
    Pull every document out of ChromaDB and build a BM25 index over them.
    Called once and cached.
    """
    global _bm25_index, _bm25_corpus

    from rank_bm25 import BM25Okapi

    vs = load_vectorstore()
    # Chroma's get() returns all stored chunks
    result = vs._collection.get(include=["documents", "metadatas"])

    _bm25_corpus = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(result["documents"], result["metadatas"])
    ]

    tokenised = [doc.page_content.lower().split() for doc in _bm25_corpus]
    _bm25_index = BM25Okapi(tokenised)
    return _bm25_index, _bm25_corpus


def _get_bm25():
    global _bm25_index, _bm25_corpus
    if _bm25_index is None:
        _build_bm25_index()
    return _bm25_index, _bm25_corpus


# ─────────────────────────────────────────────────────────────────────────────
# Individual retrievers
# ─────────────────────────────────────────────────────────────────────────────

def dense_retrieve(query: str, k: int = 10) -> List[tuple]:
    """Return top-k (Document, score) tuples by embedding similarity from Chroma."""
    vs = load_vectorstore()
    return vs.similarity_search_with_score(query, k=k)


def sparse_retrieve(query: str, k: int = 10) -> List[Document]:
    """Return top-k documents by BM25 keyword score."""
    bm25, corpus = _get_bm25()
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    ranked = sorted(zip(scores, corpus), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:k]]


# ─────────────────────────────────────────────────────────────────────────────
# Reciprocal Rank Fusion
# ─────────────────────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    dense_results: List[tuple],   # List of (Document, score)
    sparse_results: List[Document],
    k: int = 60,
) -> List[tuple]:
    """
    Fuse dense and sparse ranked lists using RRF.
    Returns List of (Document, rrf_score) sorted descending.
    Dense similarity score is preserved on the Document for downstream use.
    """
    rrf_scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}
    sim_scores: dict[str, float] = {}

    # Dense list — (Document, chroma_distance)
    for rank, (doc, sim) in enumerate(dense_results, start=1):
        key = doc.page_content
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
        doc_map[key] = doc
        sim_scores[key] = round(float(sim), 4)

    # Sparse list — Documents only
    for rank, doc in enumerate(sparse_results, start=1):
        key = doc.page_content
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
        if key not in doc_map:
            doc_map[key] = doc
            sim_scores[key] = None  # no dense score for sparse-only hits

    sorted_keys = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
    return [(doc_map[key], rrf_scores[key], sim_scores.get(key)) for key in sorted_keys]


# ─────────────────────────────────────────────────────────────────────────────
# Cross-encoder reranker — optional second-pass re-scoring
# ─────────────────────────────────────────────────────────────────────────────

def _get_cross_encoder():
    """Load and cache the cross-encoder model. Returns None on import failure."""
    global _cross_encoder
    if _cross_encoder is not None:
        return _cross_encoder
    try:
        from sentence_transformers import CrossEncoder
        _cross_encoder = CrossEncoder(_CROSS_ENCODER_MODEL)
        return _cross_encoder
    except Exception:
        return None


def rerank(query: str, candidates: List[tuple], top_k: int) -> List[tuple]:
    """
    Re-score (doc, rrf_score, sim_score) tuples with a cross-encoder for
    more precise relevance ordering.  Falls back to RRF order if model
    unavailable or candidate list is too small to be worth re-scoring.
    """
    model = _get_cross_encoder()
    if model is None or len(candidates) < 2:
        return candidates[:top_k]

    pairs = [(query, doc.page_content) for doc, _, __ in candidates]
    ce_scores = model.predict(pairs)  # shape (n,)

    # Zip CE scores with original tuples and re-sort
    scored = sorted(
        zip(ce_scores, candidates),
        key=lambda x: x[0],
        reverse=True,
    )
    return [item for _, item in scored[:top_k]]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def hybrid_search(query: str, k: int = 5) -> List[tuple]:
    """
    Perform hybrid search: dense + sparse retrieval fused with RRF.

    Returns:
        List of (Document, rrf_score, similarity_score) tuples, length k.
        similarity_score is the raw Chroma L2 distance (None for sparse-only hits).
    """
    fetch_k = max(k * 3, 15)

    dense_results = dense_retrieve(query, k=fetch_k)
    sparse_results = sparse_retrieve(query, k=fetch_k)

    fused = reciprocal_rank_fusion(dense_results, sparse_results)

    # Cross-encoder rerank: pass 3× candidates so the CE sees more options
    return rerank(query, fused[: k * 3], top_k=k)


def invalidate_bm25_cache():
    """Call this after re-ingesting documents to rebuild the BM25 index."""
    global _bm25_index, _bm25_corpus
    _bm25_index = None
    _bm25_corpus = []
