"""
Context Metrics
===============
Measures how well the retrieved context supports answering the question.

1. context_relevance   — LLM-judge: are the retrieved chunks relevant to the query?
2. context_coverage    — % of expected keywords found in the retrieved context
                         (proxy for "did we retrieve everything needed?")
3. avg_similarity_score — raw average cosine distance; lower = more similar

context_relevance uses an LLM judge and is only computed when use_llm_judge=True.
context_coverage and avg_similarity_score are always computed (no LLM calls needed).
"""

from typing import List, Dict
from evals.metrics.judge import judge as _judge


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_context_text(response: dict) -> str:
    """Concatenate all retrieved chunk page_content values into one string."""
    chunks = []
    for doc in response.get("retrieval", {}).get("documents", []):
        text = doc.get("page_content", "")
        if text:
            chunks.append(text)
    return "\n\n".join(chunks)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def avg_similarity_score(results: List[Dict]) -> float:
    """
    Average cosine distance across all retrieved documents.
    Lower = more similar. A well-tuned retriever should stay below 0.8.
    """
    all_scores = []
    for r in results:
        for doc in r["response"].get("retrieval", {}).get("documents", []):
            score = doc.get("similarity_score")
            if score is not None:
                all_scores.append(score)
    return round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0


def context_coverage(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of expected keywords that appear in the retrieved context (not the answer).
    High = the retriever is pulling in chunks that contain the necessary information.
    Low = the answer may be generated from insufficient context.
    """
    if not results:
        return 0.0
    total_kw = 0
    found_kw = 0
    for r, item in zip(results, dataset):
        context_text = _get_context_text(r["response"]).lower()
        keywords = item.get("expected_keywords") or []
        if not keywords and item.get("expected_answer"):
            stopwords = {"that", "this", "with", "from", "have", "will", "your", "they",
                         "been", "were", "what", "when", "where", "which", "while",
                         "their", "there", "after", "before", "about", "also"}
            keywords = [
                w for w in item["expected_answer"].lower().split()
                if len(w) >= 4 and w.isalpha() and w not in stopwords
            ]
        for kw in keywords:
            total_kw += 1
            if kw.lower() in context_text:
                found_kw += 1
    return round(found_kw / total_kw * 100, 2) if total_kw else 0.0


def context_relevance(results: List[Dict], dataset: List[Dict]) -> float:
    """
    LLM-judge: How relevant is the retrieved context to the query?
    Score 0–1 averaged across all items.
    1.0 = context is perfectly targeted; 0.0 = context is irrelevant noise.
    """
    scores = []
    for r, item in zip(results, dataset):
        query = item.get("question", item.get("query", ""))
        context_text = _get_context_text(r["response"])
        if not context_text:
            continue
        prompt = (
            f"QUESTION: {query}\n\n"
            f"RETRIEVED CONTEXT:\n{context_text}\n\n"
            "Evaluate context relevance:\n"
            "- Does this context contain the information needed to answer the question?\n"
            "- Is most of the context on-topic or is it mostly noise?\n"
            "- Would a human be able to answer the question accurately using only this context?\n"
            "Score using the 1–5 rubric."
        )
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_context_metrics(
    results: List[Dict],
    dataset: List[Dict],
    use_llm_judge: bool = False,
) -> Dict:
    metrics: Dict = {
        "avg_similarity_score": avg_similarity_score(results),
        "context_coverage": context_coverage(results, dataset),
    }
    if use_llm_judge:
        metrics["context_relevance"] = context_relevance(results, dataset)
    return metrics
