"""
End-to-End Metrics
==================
Measures overall pipeline success from the user's perspective.

1. task_success_rate    — Did the assistant fulfil the user's intent? (rule-based, no LLM)
2. not_found_false_positive_rate — % of in-scope questions incorrectly refused
3. source_hit_rate      — % of answers backed by the expected source document
4. llm_judge_score      — LLM holistic judge: overall answer quality 0–1
                          (only computed when use_llm_judge=True)

These metrics sit at the top of the eval pyramid and are used in CI pass/fail gates.
"""

from typing import List, Dict
from evals.metrics.judge import judge as _judge


NOT_FOUND_PHRASE = "i could not find"

# Types that should return "not found" — used by unanswerable_awareness_rate
UNANSWERABLE_TYPES = {"out_of_scope", "adversarial"}

# Pass/fail thresholds used by run_ci() in run_evals.py
THRESHOLDS = {
    "task_success_rate": 80.0,              # %
    "source_hit_rate": 70.0,                # %
    "not_found_false_positive_rate": 10.0,  # % (lower is better — this is a MAX)
    "unanswerable_awareness_rate": 70.0,    # %
    "llm_judge_score": 0.70,                # 0–1
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _is_unanswerable(item: Dict) -> bool:
    """True when the expected answer is a not-found response or type is unanswerable."""
    if item.get("type") in UNANSWERABLE_TYPES:
        return True
    expected = (item.get("expected_answer") or "").lower()
    return expected.startswith("not found")


def task_success_rate(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of answerable queries where the assistant returned a real, keyword-matching answer.
    Unanswerable/out-of-scope items are excluded (they're scored by unanswerable_awareness_rate).
    High = pipeline successfully fulfils user intent end-to-end.
    """
    if not results:
        return 0.0
    successes = 0
    total = 0
    for r, item in zip(results, dataset):
        if _is_unanswerable(item):
            continue   # handled by unanswerable_awareness_rate
        total += 1
        answer = (r["response"].get("answer") or "").lower()
        if NOT_FOUND_PHRASE in answer or not answer:
            continue
        keywords = item.get("expected_keywords") or []
        if not keywords:
            # Fall back: look for significant words from expected_answer in the actual answer
            stopwords = {"that", "this", "with", "from", "have", "will", "your", "they",
                         "been", "were", "what", "when", "where", "which", "while",
                         "their", "there", "after", "before", "about", "also", "only"}
            keywords = [
                w for w in (item.get("expected_answer") or "").lower().split()
                if len(w) >= 4 and w.isalpha() and w not in stopwords
            ]
        if not keywords or any(kw.lower() in answer for kw in keywords):
            successes += 1
    return round(successes / total * 100, 2) if total else 0.0


def not_found_false_positive_rate(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of in-scope (answerable) questions where the assistant incorrectly said it could not find.
    Low is better. High = retriever is missing relevant chunks for real questions.
    """
    if not results:
        return 0.0
    false_positives = 0
    total_in_scope = 0
    for r, item in zip(results, dataset):
        if _is_unanswerable(item):
            continue  # these SHOULD say not-found, so they don't count as false positives
        total_in_scope += 1
        answer = (r["response"].get("answer") or "").lower()
        if NOT_FOUND_PHRASE in answer:
            false_positives += 1
    return round(false_positives / total_in_scope * 100, 2) if total_in_scope else 0.0


def source_hit_rate(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of answers where at least one retrieved document came from the expected source.
    High = retrieval is pulling from the correct knowledge-base document.
    """
    if not results:
        return 0.0
    hits = 0
    total = 0
    for r, item in zip(results, dataset):
        expected = (item.get("source_doc") or item.get("expected_source") or "").lower()
        if not expected:
            continue
        sources = [
            doc["metadata"].get("source", "").lower()
            for doc in r["response"].get("retrieval", {}).get("documents", [])
        ]
        if any(expected in src for src in sources):
            hits += 1
        total += 1
    return round(hits / total * 100, 2) if total else 0.0


def unanswerable_awareness_rate(results: List[Dict], dataset: List[Dict]) -> float:
    """
    % of out_of_scope / adversarial questions where the assistant correctly
    returned a 'not found' response instead of hallucinating an answer.
    High = the system knows what it doesn't know.
    """
    if not results:
        return 0.0
    correct = 0
    total = 0
    for r, item in zip(results, dataset):
        if item.get("type") not in UNANSWERABLE_TYPES:
            continue
        total += 1
        answer = (r["response"].get("answer") or "").lower()
        if NOT_FOUND_PHRASE in answer or not answer:
            correct += 1
    return round(correct / total * 100, 2) if total else None  # None = no unanswerable items in this dataset


def llm_judge_score(results: List[Dict], dataset: List[Dict]) -> float:
    """
    LLM holistic judge: given the question and answer, how good is the overall response?
    Score 0–1 averaged across all items.
    Considers relevance, completeness, and tone for an internal knowledge assistant.
    """
    scores = []
    for r, item in zip(results, dataset):
        question = item.get("question", item.get("query", ""))
        answer = r["response"].get("answer") or ""
        if not answer:
            scores.append(0.0)
            continue
        prompt = (
            f"EMPLOYEE QUESTION: {question}\n\n"
            f"ASSISTANT ANSWER:\n{answer}\n\n"
            "Evaluate overall answer quality for an internal company knowledge-base assistant:\n"
            "- Is the answer relevant and directly addresses the question?\n"
            "- Is the answer complete — does it cover all key aspects?\n"
            "- Is the tone professional and clear?\n"
            "- Are there any hallucinations or unsupported claims?\n"
            "Score using the 1–5 rubric."
        )
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_e2e_metrics(
    results: List[Dict],
    dataset: List[Dict],
    use_llm_judge: bool = False,
) -> Dict:
    metrics: Dict = {
        "task_success_rate": task_success_rate(results, dataset),
        "not_found_false_positive_rate": not_found_false_positive_rate(results, dataset),
        "source_hit_rate": source_hit_rate(results, dataset),
        "unanswerable_awareness_rate": unanswerable_awareness_rate(results, dataset),
    }
    if use_llm_judge:
        metrics["llm_judge_score"] = llm_judge_score(results, dataset)
    return metrics


def check_thresholds(e2e: Dict) -> List[str]:
    """
    Return a list of failure messages for any metric that breaches its CI threshold.
    Empty list = all gates passed.
    """
    failures = []
    for metric, threshold in THRESHOLDS.items():
        value = e2e.get(metric)
        if value is None:
            continue
        # not_found_false_positive_rate is a MAX threshold (lower is better)
        if metric == "not_found_false_positive_rate":
            if value > threshold:
                failures.append(f"FAIL  {metric}: {value} > allowed max {threshold}")
        else:
            if value < threshold:
                failures.append(f"FAIL  {metric}: {value} < required min {threshold}")
    return failures
