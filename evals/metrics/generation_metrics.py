"""
Generation Metrics
==================
Measures the quality of the LLM's generated answer.

1. keyword_coverage     — % of expected keywords present in the answer (no LLM needed)
2. answer_found_rate    — % of in-scope queries where an answer was actually returned
3. faithfulness_score   — LLM-judge: is the answer grounded in the retrieved context?
4. answer_relevance_score — LLM-judge: does the answer actually address the question?

LLM-judge functions are only called when `use_llm_judge=True` to keep local runs cheap.
"""

from typing import List, Dict
from evals.metrics.judge import judge as _judge


NOT_FOUND_PHRASE = "i could not find"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _context_from_response(response: dict) -> str:
    return "\n\n".join(
        doc.get("page_content", "")
        for doc in response.get("retrieval", {}).get("documents", [])
        if doc.get("page_content")
    )


# ---------------------------------------------------------------------------
# Non-LLM metrics
# ---------------------------------------------------------------------------

def keyword_coverage(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of expected keywords found across all answers.
    High = answers are complete and contain the right terminology.
    """
    if not results:
        return 0.0
    total_kw = 0
    found_kw = 0
    for r, item in zip(results, dataset):
        answer = (r["response"].get("answer") or "").lower()
        keywords = item.get("expected_keywords") or []
        # Fall back: derive keywords from expected_answer (words ≥ 4 chars, skip stopwords)
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
            if kw.lower() in answer:
                found_kw += 1
    return round(found_kw / total_kw * 100, 2) if total_kw else 0.0


def answer_found_rate(results: List[Dict]) -> float:
    """
    % of queries where the assistant returned an actual answer (not "could not find").
    High = assistant is successfully answering employee questions.
    """
    if not results:
        return 0.0
    found = sum(
        1 for r in results
        if r["response"].get("answer")
        and NOT_FOUND_PHRASE not in r["response"]["answer"].lower()
    )
    return round(found / len(results) * 100, 2)


# ---------------------------------------------------------------------------
# LLM-judge metrics
# ---------------------------------------------------------------------------

def faithfulness_score(results: List[Dict], dataset: List[Dict]) -> float:
    """
    LLM-judge (1–5 rubric): Is every claim in the answer grounded in the retrieved context?
    1.0 = fully grounded; 0.0 = hallucinated.
    """
    scores = []
    for r, item in zip(results, dataset):
        answer = r["response"].get("answer") or ""
        context = _context_from_response(r["response"])
        if not answer or not context:
            continue
        prompt = (
            f"CONTEXT (retrieved documents):\n{context}\n\n"
            f"ANSWER TO EVALUATE:\n{answer}\n\n"
            "Evaluate faithfulness:\n"
            "- Is every claim in the answer directly supported by the context above?\n"
            "- Are there any hallucinated facts not present in the context?\n"
            "- Are there invented numbers, dates, names, or policy details?\n"
            "Score using the 1–5 rubric."
        )
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


def answer_relevance_score(results: List[Dict], dataset: List[Dict]) -> float:
    """
    LLM-judge (1–5 rubric): Does the answer directly address the question?
    1.0 = perfectly on-point; 0.0 = completely off-topic.
    """
    scores = []
    for r, item in zip(results, dataset):
        question = item.get("question", item.get("query", ""))
        answer = r["response"].get("answer") or ""
        if not answer:
            continue
        prompt = (
            f"QUESTION: {question}\n\n"
            f"ANSWER TO EVALUATE:\n{answer}\n\n"
            "Evaluate relevance:\n"
            "- Does the answer directly address the specific question asked?\n"
            "- Is all the information in the answer actually relevant to the question?\n"
            "- Does it stay focused or wander off-topic?\n"
            "Score using the 1–5 rubric."
        )
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


def correctness_score(results: List[Dict], dataset: List[Dict]) -> float:
    """
    LLM-judge (1–5 rubric): Is the answer factually correct relative to expected key facts?
    1.0 = all key facts correct; 0.0 = factually wrong or missing critical facts.
    """
    scores = []
    for r, item in zip(results, dataset):
        question = item.get("question", item.get("query", ""))
        answer = r["response"].get("answer") or ""
        expected_keywords = item.get("expected_keywords") or []
        expected_answer = item.get("expected_answer", "")
        if not answer or (not expected_keywords and not expected_answer):
            continue
        if expected_keywords:
            reference = "EXPECTED KEY FACTS / TERMS a correct answer must include:\n" + ", ".join(expected_keywords)
        else:
            reference = "EXPECTED ANSWER (ground truth):\n" + expected_answer
        prompt = (
            f"QUESTION: {question}\n\n"
            f"{reference}\n\n"
            f"ACTUAL ANSWER TO EVALUATE:\n{answer}\n\n"
            "Evaluate correctness:\n"
            "- Are all the expected key facts present and accurate?\n"
            "- Are any key facts missing entirely?\n"
            "- Are any facts stated incorrectly (wrong numbers, wrong names, wrong rules)?\n"
            "Score using the 1–5 rubric."
        )
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_generation_metrics(
    results: List[Dict],
    dataset: List[Dict],
    use_llm_judge: bool = False,
) -> Dict:
    metrics: Dict = {
        "answer_found_rate": answer_found_rate(results),
        "keyword_coverage": keyword_coverage(results, dataset),
    }
    if use_llm_judge:
        metrics["faithfulness_score"] = faithfulness_score(results, dataset)
        metrics["answer_relevance_score"] = answer_relevance_score(results, dataset)
        metrics["correctness_score"] = correctness_score(results, dataset)
    return metrics
