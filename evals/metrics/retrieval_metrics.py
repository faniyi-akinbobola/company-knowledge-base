"""
Retrieval Metrics
=================
Measures how well the vector store fetches the right documents.

1. recall_at_k    — Was the expected source retrieved within top-k results?
2. precision_at_k — Of the top-k docs retrieved, what fraction are relevant?
3. mrr            — Mean Reciprocal Rank: how high does the first relevant doc rank?

All functions accept a flat list of result dicts produced by run_dataset():
  result = {"item": dataset_item, "response": answer_query(...)}
"""

from typing import List, Dict


SIMILARITY_THRESHOLD = 1.5  # ChromaDB L2 distance — lower is more similar; < 1.5 is relevant


def _get_retrieved_sources(response: dict) -> List[str]:
    """Extract normalised source paths from a response dict."""
    return [
        doc["metadata"].get("source", "").lower()
        for doc in response.get("retrieval", {}).get("documents", [])
    ]


def _get_scores(response: dict) -> List[float]:
    return [
        doc.get("similarity_score") or 1.0
        for doc in response.get("retrieval", {}).get("documents", [])
    ]


# ---------------------------------------------------------------------------
# Recall@k
# ---------------------------------------------------------------------------

def recall_at_k(results: List[Dict], k: int = 5) -> float:
    """
    % of queries where the expected source appeared in the top-k retrieved docs.
    High = retriever reliably surfaces the right document.
    """
    if not results:
        return 0.0
    hits = 0
    total = 0
    for r in results:
        expected = (r["item"].get("source_doc") or r["item"].get("expected_source") or "").lower()
        if not expected:
            continue
        sources = _get_retrieved_sources(r["response"])[:k]
        if any(expected in src for src in sources):
            hits += 1
        total += 1
    return round(hits / total * 100, 2) if total else 0.0


# ---------------------------------------------------------------------------
# Precision@k
# ---------------------------------------------------------------------------

def precision_at_k(results: List[Dict], k: int = 5, threshold: float = SIMILARITY_THRESHOLD) -> float:
    """
    Of the top-k retrieved chunks, what % have a similarity score below `threshold`
    (i.e. are genuinely close to the query)?
    High = retriever avoids pulling in noisy, off-topic chunks.
    """
    total = 0
    relevant = 0
    for r in results:
        for score in _get_scores(r["response"])[:k]:
            total += 1
            if score < threshold:
                relevant += 1
    return round(relevant / total * 100, 2) if total else 0.0


# ---------------------------------------------------------------------------
# MRR — Mean Reciprocal Rank
# ---------------------------------------------------------------------------

def mrr(results: List[Dict]) -> float:
    """
    Mean Reciprocal Rank of the first relevant (expected-source) document.
    1.0 = always retrieved first; 0.5 = first relevant doc is at rank 2; etc.
    High = relevant document appears near the top of retrieved results.
    """
    if not results:
        return 0.0
    rr_scores = []
    for r in results:
        expected = (r["item"].get("source_doc") or r["item"].get("expected_source") or "").lower()
        if not expected:
            continue
        sources = _get_retrieved_sources(r["response"])
        rr = 0.0
        for rank, src in enumerate(sources, 1):
            if expected in src:
                rr = 1.0 / rank
                break
        rr_scores.append(rr)
    return round(sum(rr_scores) / len(rr_scores), 4) if rr_scores else 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_retrieval_metrics(results: List[Dict], k: int = 5) -> Dict:
    return {
        "recall_at_k": recall_at_k(results, k=k),
        "precision_at_k": precision_at_k(results, k=k),
        "mrr": mrr(results),
    }
