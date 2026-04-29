"""
Evaluation Runner
=================
Entry point for all RAG pipeline evaluations.

Usage:
    uv run python evals/runners/run_evals.py --mode local
    uv run python evals/runners/run_evals.py --mode local --llm-judge
    uv run python evals/runners/run_evals.py --mode ci
    uv run python evals/runners/run_evals.py --mode ci --llm-judge

Modes:
    local  — run queries locally, print a formatted report, save JSON to evals/results/
    ci     — local run + push dataset + results to LangSmith, exit 1 if thresholds fail

Environment variables required:
    OPENAI_API_KEY      — for the RAG pipeline + LLM-judge
    LANGCHAIN_API_KEY   — for LangSmith tracing & dataset upload (ci mode)
    LANGCHAIN_PROJECT   — LangSmith project name (optional, defaults to "company-kb-evals")
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── project root on sys.path ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.answer import answer_query  # noqa: E402
from evals.metrics.retrieval_metrics import run_retrieval_metrics
from evals.metrics.generation_metrics import run_generation_metrics
from evals.metrics.context_metrics import run_context_metrics
from evals.metrics.e2e_metrics import run_e2e_metrics, check_thresholds

DATASETS_DIR = PROJECT_ROOT / "evals" / "datasets"
RESULTS_DIR = PROJECT_ROOT / "evals" / "results"

LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "company-kb-evals")


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


def run_dataset(dataset: list, label: str) -> list:
    """Call answer_query() for every item and return a list of result dicts."""
    results = []
    total = len(dataset)
    for i, item in enumerate(dataset, 1):
        query = item.get("question", item.get("question", item.get("query", "")))
        print(f"  [{i:>2}/{total}] {query[:72]}...")
        try:
            response = answer_query(query, history=[])
        except Exception as exc:
            response = {
                "answer": None,
                "retrieval": {"documents": []},
                "error": {"message": str(exc), "type": type(exc).__name__},
            }
        results.append({"item": item, "response": response})
    return results


def compute_all_metrics(qa_results: list, qa_dataset: list, use_llm_judge: bool) -> dict:
    return {
        "retrieval": run_retrieval_metrics(qa_results),
        "generation": run_generation_metrics(qa_results, qa_dataset, use_llm_judge),
        "context": run_context_metrics(qa_results, qa_dataset, use_llm_judge),
        "e2e": run_e2e_metrics(qa_results, qa_dataset, use_llm_judge),
    }


def compute_edge_metrics(edge_results: list, edge_dataset: list, use_llm_judge: bool) -> dict:
    """Metrics computed only on the edge-case dataset (robustness checks)."""
    from evals.metrics.e2e_metrics import (
        task_success_rate,
        unanswerable_awareness_rate,
        not_found_false_positive_rate,
    )
    metrics = {
        "unanswerable_awareness_rate": unanswerable_awareness_rate(edge_results, edge_dataset),
        "not_found_false_positive_rate": not_found_false_positive_rate(edge_results, edge_dataset),
        "task_success_rate": task_success_rate(edge_results, edge_dataset),
    }
    if use_llm_judge:
        from evals.metrics.e2e_metrics import llm_judge_score
        metrics["llm_judge_score"] = llm_judge_score(edge_results, edge_dataset)
    return metrics


def build_report(qa_results, edge_results, metrics, edge_metrics, qa_dataset, edge_dataset, use_llm_judge) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return {
        "timestamp": timestamp,
        "config": {
            "qa_cases": len(qa_dataset),
            "edge_cases": len(edge_dataset),
            "use_llm_judge": use_llm_judge,
        },
        "metrics": metrics,
        "edge_metrics": edge_metrics,
        "qa_results": [
            {
                "query": r["item"].get("question", r["item"].get("query", "")),
                "answer": r["response"].get("answer", ""),
                "error": r["response"].get("error"),
                "similarity_scores": [
                    d.get("similarity_score")
                    for d in r["response"].get("retrieval", {}).get("documents", [])
                ],
            }
            for r in qa_results
        ],
        "edge_results": [
            {
                "query": r["item"].get("question", r["item"].get("query", "")),
                "type": r["item"].get("type", ""),
                "answer": r["response"].get("answer", ""),
                "error": r["response"].get("error"),
            }
            for r in edge_results
        ],
    }


def save_report(report: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"eval_{report['timestamp']}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    return out_path


def print_report(report: dict):
    metrics = report["metrics"]
    edge_metrics = report.get("edge_metrics", {})
    print("\n" + "═" * 62)
    print("  EVALUATION RESULTS — QA Dataset")
    print("═" * 62)
    sections = [
        ("Retrieval Metrics", metrics.get("retrieval", {})),
        ("Generation Metrics", metrics.get("generation", {})),
        ("Context Metrics", metrics.get("context", {})),
        ("End-to-End Metrics", metrics.get("e2e", {})),
    ]
    for title, section in sections:
        print(f"\n  {title}")
        print("  " + "─" * 40)
        for k, v in section.items():
            print(f"    {k:<38} {v}")
    if edge_metrics:
        print("\n" + "═" * 62)
        print("  EDGE-CASE ROBUSTNESS METRICS")
        print("═" * 62)
        for k, v in edge_metrics.items():
            print(f"    {k:<38} {v}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# LangSmith helpers (ci mode)
# ─────────────────────────────────────────────────────────────────────────────

def _langsmith_client():
    """Return a LangSmith Client, raising clearly if credentials are missing."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "LANGCHAIN_API_KEY is not set. "
            "Export it before running in ci mode:\n"
            "  export LANGCHAIN_API_KEY=lsv2_..."
        )
    from langsmith import Client  # lazy import — local mode has no hard dep
    return Client(api_key=api_key)


def push_dataset_to_langsmith(client, dataset: list, name: str, description: str):
    """
    Create (or reuse) a LangSmith dataset and upsert all examples.
    Returns the LangSmith Dataset object.
    """
    existing = {d.name: d for d in client.list_datasets()}
    if name in existing:
        ls_dataset = existing[name]
        print(f"  ↩  Reusing LangSmith dataset: '{name}'")
    else:
        ls_dataset = client.create_dataset(name, description=description)
        print(f"  ✚  Created LangSmith dataset: '{name}'")

    client.create_examples(
        inputs=[{"query": item.get("question", item.get("question", item.get("query", "")))} for item in dataset],
        outputs=[
            {
                "expected_keywords": item.get("expected_keywords", []),
                "expected_source": item.get("expected_source", ""),
            }
            for item in dataset
        ],
        dataset_id=ls_dataset.id,
    )
    return ls_dataset


def push_results_to_langsmith(client, report: dict, run_name: str):
    """Log a flat metric summary as a LangSmith run."""
    flat_metrics = {}
    for section_metrics in report["metrics"].values():
        flat_metrics.update(section_metrics)

    run = client.create_run(
        name=run_name,
        run_type="chain",
        project_name=LANGSMITH_PROJECT,
        inputs={"dataset": "qa_dataset", "timestamp": report["timestamp"]},
        outputs=flat_metrics,
    )
    client.update_run(run.id, end_time=datetime.utcnow(), status="success")
    print(f"  📤  Results pushed to LangSmith project '{LANGSMITH_PROJECT}' (run: {run.id})")


# ─────────────────────────────────────────────────────────────────────────────
# Mode: local
# ─────────────────────────────────────────────────────────────────────────────

def run_local(use_llm_judge: bool):
    print("=" * 62)
    print("  Mode: LOCAL")
    print("=" * 62)

    qa_dataset = load_json(DATASETS_DIR / "qa_dataset.json")
    edge_dataset = load_json(DATASETS_DIR / "edge_cases.json")

    print(f"\n▶ Running QA dataset ({len(qa_dataset)} cases)...")
    qa_results = run_dataset(qa_dataset, "qa")

    print(f"\n▶ Running edge-case dataset ({len(edge_dataset)} cases)...")
    edge_results = run_dataset(edge_dataset, "edge")

    print("\n▶ Computing metrics...")
    metrics = compute_all_metrics(qa_results, qa_dataset, use_llm_judge)
    edge_metrics = compute_edge_metrics(edge_results, edge_dataset, use_llm_judge)

    report = build_report(qa_results, edge_results, metrics, edge_metrics, qa_dataset, edge_dataset, use_llm_judge)
    out_path = save_report(report)

    print_report(report)
    print(f"✅  Report saved → {out_path}")
    print("=" * 62)


# ─────────────────────────────────────────────────────────────────────────────
# Mode: ci
# ─────────────────────────────────────────────────────────────────────────────

def run_ci(use_llm_judge: bool):
    print("=" * 62)
    print("  Mode: CI  (LangSmith enabled)")
    print("=" * 62)

    # Enable LangSmith tracing for all LLM calls made during eval
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", LANGSMITH_PROJECT)

    client = _langsmith_client()

    qa_dataset = load_json(DATASETS_DIR / "qa_dataset.json")
    edge_dataset = load_json(DATASETS_DIR / "edge_cases.json")

    # Sync datasets to LangSmith
    print("\n▶ Syncing datasets to LangSmith...")
    push_dataset_to_langsmith(
        client, qa_dataset,
        name="company-kb-qa",
        description="Factual QA test cases for the ApexTech knowledge base",
    )
    push_dataset_to_langsmith(
        client, edge_dataset,
        name="company-kb-edge-cases",
        description="Edge cases: greetings, out-of-scope, vague, follow-up queries",
    )

    print(f"\n▶ Running QA dataset ({len(qa_dataset)} cases)...")
    qa_results = run_dataset(qa_dataset, "qa")

    print(f"\n▶ Running edge-case dataset ({len(edge_dataset)} cases)...")
    edge_results = run_dataset(edge_dataset, "edge")

    print("\n▶ Computing metrics...")
    metrics = compute_all_metrics(qa_results, qa_dataset, use_llm_judge)
    edge_metrics = compute_edge_metrics(edge_results, edge_dataset, use_llm_judge)

    report = build_report(qa_results, edge_results, metrics, edge_metrics, qa_dataset, edge_dataset, use_llm_judge)
    out_path = save_report(report)

    # Push metric summary to LangSmith
    print("\n▶ Pushing results to LangSmith...")
    push_results_to_langsmith(client, report, run_name=f"eval-{report['timestamp']}")

    print_report(report)
    print(f"✅  Report saved → {out_path}")

    # ── CI gate ───────────────────────────────────────────────────────────
    failures = check_thresholds(metrics.get("e2e", {}))
    if failures:
        print("\n❌  CI GATE FAILURES:")
        for msg in failures:
            print(f"    {msg}")
        print("=" * 62)
        sys.exit(1)

    print("✅  All CI thresholds passed.")
    print("=" * 62)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run RAG pipeline evaluations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run python evals/runners/run_evals.py --mode local\n"
            "  uv run python evals/runners/run_evals.py --mode local --llm-judge\n"
            "  uv run python evals/runners/run_evals.py --mode ci\n"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["local", "ci"],
        default="local",
        help="local = run locally and print report; ci = local + LangSmith + threshold gates",
    )
    parser.add_argument(
        "--llm-judge",
        action="store_true",
        help="Enable LLM-as-judge metrics (faithfulness, context relevance, e2e score). "
             "Incurs extra OpenAI API calls.",
    )
    args = parser.parse_args()

    if args.mode == "local":
        run_local(use_llm_judge=args.llm_judge)
    elif args.mode == "ci":
        run_ci(use_llm_judge=args.llm_judge)


if __name__ == "__main__":
    main()
