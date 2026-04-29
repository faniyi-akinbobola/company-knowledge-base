# 🏢 ApexTech Solutions — Company Knowledge Base

An internal AI-powered assistant that allows ApexTech employees to query company documentation using natural language. Built with **RAG (Retrieval-Augmented Generation)**, it retrieves relevant information from internal documents and generates accurate, sourced answers.

---

## 🏗️ Architecture

```
Query
  │
  ▼
Query Rewriter (gpt-4o-mini)        ← Rewrites vague/conversational queries
  │
  ▼
Hybrid Search                        ← Dense (Chroma) + Sparse (BM25) fused via RRF
  │
  ▼
Cross-Encoder Reranker               ← ms-marco-MiniLM-L-6-v2 reranks top-k chunks
  │
  ▼
LLM (gpt-4.1-mini) + System Prompt  ← Grounded answer from retrieved context
  │
  ▼
Answer + Sources
```

---

## 📁 Project Structure

```
company-knowledge-base/
├── UI/
│   └── ui.py                   # Chainlit UI (User mode)
├── rag/
│   ├── answer.py               # Full RAG pipeline
│   ├── hybrid_search.py        # Dense + BM25 + RRF + cross-encoder reranker
│   ├── query_rewriter.py       # LLM query rewriter
│   ├── ingest.py               # Document ingestion
│   ├── chunking.py             # Text splitting
│   ├── embedding.py            # HuggingFace embeddings
│   └── vectorstore.py          # Chroma vector store
├── llm/
│   ├── llm.py                  # LLM initialisation
│   └── prompt.py               # System prompt template
├── evals/
│   ├── datasets/
│   │   ├── qa_dataset.json     # 60 QA pairs (easy + hard)
│   │   └── edge_cases.json     # 20 adversarial / edge cases
│   ├── metrics/
│   │   ├── retrieval_metrics.py    # recall@k, precision@k, MRR
│   │   ├── generation_metrics.py   # faithfulness, relevance, correctness
│   │   ├── context_metrics.py      # context coverage, context relevance
│   │   └── e2e_metrics.py          # task success, unanswerable awareness, CI gates
│   ├── runners/
│   │   └── run_evals.py        # local + ci modes with LangSmith integration
│   └── results/                # Timestamped JSON eval reports
├── data/
│   ├── raw/                    # Source .md documents (canonical)
│   └── vector_db/              # Chroma persistent store
├── main.py                     # Entry point — ingest check + UI launch
└── chainlit.md                 # Chainlit welcome screen
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/faniyi-akinbobola/company-knowledge-base.git
cd company-knowledge-base
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=company-knowledge-base
```

### 4. Run the app

```bash
uv run python main.py
```

This will:

- ✅ Check if the vector store exists
- ✅ Auto-ingest documents if not found
- ✅ Launch the Chainlit UI at `http://localhost:8000`

---

## 🧪 Evals

```bash
# Fast local run — no LLM judge
uv run python evals/runners/run_evals.py --mode local

# With LLM-as-judge (faithfulness, correctness, relevance, hallucination)
uv run python evals/runners/run_evals.py --mode local --llm-judge

# CI mode — requires LANGCHAIN_API_KEY, exits with code 1 on threshold breach
uv run python evals/runners/run_evals.py --mode ci
```

### Latest eval results

| Metric                        | Score | CI Threshold |
| ----------------------------- | ----- | ------------ |
| recall@k                      | 87.5% | —            |
| precision@k                   | 98.0% | —            |
| MRR                           | 0.77  | —            |
| answer_found_rate             | 85.0% | —            |
| faithfulness                  | 0.81  | —            |
| answer_relevance              | 0.85  | —            |
| correctness                   | 0.62  | —            |
| task_success_rate             | 80.4% | ≥ 80% ✅     |
| unanswerable_awareness        | 100%  | ≥ 70% ✅     |
| not_found_false_positive_rate | 8.9%  | ≤ 10% ✅     |
| llm_judge_score               | 0.83  | ≥ 0.70 ✅    |

---

## 🔭 LangSmith Tracing

All LLM calls (UI + evals) are automatically traced to LangSmith when `LANGCHAIN_TRACING_V2=true` is set. No extra code required. View traces at [smith.langchain.com](https://smith.langchain.com).

---

## 🚀 Deploying to HuggingFace Spaces

### 1. Create a new Space

Go to [huggingface.co/new-space](https://huggingface.co/new-space):

- **SDK**: Docker
- **Visibility**: Private (internal tool)
- **Hardware**: CPU Basic (free) — the app peaks at ~470MB RAM, well within limits

### 2. Push this repo to your Space

```bash
# Add your Space as a remote (replace YOUR_USERNAME and SPACE_NAME)
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push master to the Space
git push space master
```

HuggingFace will automatically build the Docker image and launch the app.

### 3. Set Secrets

In your Space → **Settings → Repository secrets**, add:

| Secret                 | Value                               |
| ---------------------- | ----------------------------------- |
| `OPENAI_API_KEY`       | `sk-...`                            |
| `LANGCHAIN_API_KEY`    | `lsv2_...` (optional, for tracing)  |
| `LANGCHAIN_TRACING_V2` | `true` (optional)                   |
| `LANGCHAIN_PROJECT`    | `company-knowledge-base` (optional) |

### What happens at build time

The `Dockerfile` does the following during image build (no secrets needed):

1. Installs all Python dependencies via `uv sync`
2. Downloads and caches both HuggingFace models (`all-MiniLM-L6-v2`, `ms-marco-MiniLM-L-6-v2`)
3. Runs `rag/ingest.py` to build the ChromaDB vector store from the raw documents
4. Bakes everything into the image → **zero cold-start delay**

---
