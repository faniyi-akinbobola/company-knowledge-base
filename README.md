---
title: ApexTech Knowledge Base
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

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

### Step 1 — Create a new Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Owner**: your HuggingFace username or org
   - **Space name**: e.g. `apextech-knowledge-base`
   - **License**: choose one (e.g. MIT)
   - **SDK**: select **Docker**
   - **Visibility**: **Private** (this is an internal tool)
   - **Hardware**: CPU Basic — free tier (app peaks at ~470MB RAM ✅)
3. Click **Create Space**

---

### Step 2 — Add your OpenAI API key as a Secret

> ⚠️ Do this **before** pushing code — the build needs it to run the LLM.

1. In your Space, go to **Settings** (top right)
2. Scroll to **Repository secrets**
3. Click **New secret** and add:

| Name                   | Value                                               |
| ---------------------- | --------------------------------------------------- |
| `OPENAI_API_KEY`       | `sk-...` your OpenAI key                            |
| `LANGCHAIN_API_KEY`    | `lsv2_...` _(optional — enables LangSmith tracing)_ |
| `LANGCHAIN_TRACING_V2` | `true` _(optional)_                                 |
| `LANGCHAIN_PROJECT`    | `company-knowledge-base` _(optional)_               |

---

### Step 3 — Push your code to the Space

Run these commands from your project root:

```bash
# One-time setup: add the Space as a git remote
# Replace YOUR_USERNAME and SPACE_NAME with your actual values
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push your master branch to the Space
git push space master
```

> If you get an authentication error, use a HuggingFace token:
> `git remote set-url space https://YOUR_HF_TOKEN@huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
> Generate a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) with **write** access.

---

### Step 4 — Monitor the build

1. Go to your Space page on HuggingFace
2. Click the **Build logs** tab
3. The build will:
   - Install all Python dependencies (~3–5 min)
   - Download the HuggingFace embedding + reranker models (~2 min)
   - Run `rag/ingest.py` to build the vector database (~1 min)
   - Start the Chainlit server on port 7860
4. When the build is complete the Space shows **Running** (green)
5. Click the app URL to open the assistant

Total first-build time: **~10–15 minutes**. Subsequent pushes are faster due to Docker layer caching.

---

### Step 5 — Updating the app

Every time you push to the `space` remote, HuggingFace rebuilds and redeploys automatically:

```bash
# Make your changes, commit, then:
git push space master
```

---

### What the Dockerfile does at build time

| Step            | What happens                                                         | Secrets needed?     |
| --------------- | -------------------------------------------------------------------- | ------------------- |
| `uv sync`       | Installs all Python dependencies                                     | No                  |
| Download models | Pulls `all-MiniLM-L6-v2` + `ms-marco-MiniLM-L-6-v2` from HuggingFace | No                  |
| `rag/ingest.py` | Builds ChromaDB vector store from raw `.md` + `.csv` docs            | No                  |
| Runtime start   | Launches Chainlit on port 7860                                       | `OPENAI_API_KEY` ✅ |

Models and vector DB are **baked into the image** — zero cold-start delay.

---
