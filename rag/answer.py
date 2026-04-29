from dotenv import load_dotenv
load_dotenv()

import re
from rag.hybrid_search import hybrid_search
from rag.query_rewriter import rewrite_query
from llm.llm import llm
from llm.prompt import SYSTEM_PROMPT_TEMPLATE

# Patterns that indicate a conversational greeting — no retrieval needed
_GREETING_RE = re.compile(
    r"^\s*(hey(\s+there)?|hi(\s+there)?|hello(\s+there)?|howdy|greetings|"
    r"good\s*(morning|afternoon|evening)|sup|what'?s\s+up)[!.,?\s]*$",
    re.IGNORECASE,
)

_GREETING_RESPONSE = (
    "Hello! 👋 I'm the ApexTech Solutions AI Assistant.\n\n"
    "I can help you with information about:\n"
    "- Company policies (remote work, expenses, HR, security)\n"
    "- Employee benefits and onboarding\n"
    "- IT support and training resources\n"
    "- The company directory and internal contacts\n\n"
    "What would you like to know?"
)


def _is_greeting(query: str) -> bool:
    return bool(_GREETING_RE.match(query.strip()))


def answer_query(query: str, history: list = None) -> dict:
    """
    Full RAG pipeline: raw query → rewrite → hybrid search → LLM → answer.
    Greetings are short-circuited — no retrieval, no LLM cost, no sources shown.
    """
    if history is None:
        history = []

    error = {"message": None, "type": None}

    # Short-circuit: greetings don't need retrieval or sources
    if _is_greeting(query):
        return {
            "query": query,
            "rewritten_query": query,
            "answer": _GREETING_RESPONSE,
            "retrieval": {"documents": [], "avg_similarity_score": 0.0},
            "error": error,
        }

    try:
        # Step 1 — Rewrite query for better retrieval
        rewritten = rewrite_query(query)

        # Step 2 — Hybrid search (dense + sparse + RRF + cross-encoder rerank)
        docs_with_scores = hybrid_search(rewritten, k=20)

        # Step 3 — Build context
        context_chunks = []
        retrieval_docs = []

        for item in docs_with_scores:
            if isinstance(item, tuple) and len(item) == 3:
                doc, rrf_score, sim_score = item
            elif isinstance(item, tuple) and len(item) == 2:
                doc, sim_score = item
                rrf_score = None
            else:
                doc = item
                rrf_score = None
                sim_score = None

            context_chunks.append(doc.page_content)
            retrieval_docs.append({
                "metadata": doc.metadata,
                "page_content": doc.page_content,
                "rrf_score": round(rrf_score, 4) if rrf_score is not None else None,
                "similarity_score": round(sim_score, 4) if sim_score is not None else None,
            })

        context = "\n\n---\n\n".join(context_chunks)

        # Step 4 — Build prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=context,
            question=query,
        )

        # Step 5 — Call LLM with conversation history (last 3 turns)
        messages = []
        for human, ai in history[-3:]:
            messages.append({"role": "user", "content": human})
            messages.append({"role": "assistant", "content": ai})
        messages.append({"role": "user", "content": prompt})

        response = llm.invoke(messages)
        answer = response.content.strip()

        return {
            "query": query,
            "rewritten_query": rewritten,
            "answer": answer,
            "retrieval": {
                "documents": retrieval_docs,
                "avg_similarity_score": (
                    sum(d["similarity_score"] for d in retrieval_docs if d["similarity_score"] is not None)
                    / max(len([d for d in retrieval_docs if d["similarity_score"] is not None]), 1)
                ),
            },
            "error": error,
        }

    except Exception as e:
        error["message"] = str(e)
        error["type"] = type(e).__name__
        return {
            "query": query,
            "rewritten_query": query,
            "answer": "",
            "retrieval": {"documents": [], "avg_similarity_score": 0.0},
            "error": error,
        }

