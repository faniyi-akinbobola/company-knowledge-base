from dotenv import load_dotenv
load_dotenv()

from rag.hybrid_search import hybrid_search
from rag.query_rewriter import rewrite_query, _rewriter_llm
from llm.llm import llm
from llm.prompt import SYSTEM_PROMPT_TEMPLATE
from langchain_core.messages import HumanMessage, SystemMessage

_GREETING_CLASSIFIER_SYSTEM = """You are a message classifier. 
Determine if the user's message is purely a social greeting with no information request.

Examples of greetings: hi, hello, hey, hey there, good morning, good day, good evening, 
howdy, what's up, yo, sup, greetings, bonjour, hola, salut, morning, evening, afternoon,
how are you, how's it going, how do you do, nice to meet you, pleased to meet you.

NOT a greeting: "hi, what is the leave policy?", "hello can you help me with expenses?"

Reply with exactly one word: YES if it is a greeting, NO if it is not."""


def _is_greeting(query: str) -> bool:
    """Use the LLM to reliably classify any greeting in any phrasing or language."""
    try:
        response = _rewriter_llm.invoke([
            SystemMessage(content=_GREETING_CLASSIFIER_SYSTEM),
            HumanMessage(content=query.strip()),
        ])
        return response.content.strip().upper().startswith("YES")
    except Exception:
        return False  # safe fallback — never skip retrieval on error


def answer_query(query: str, history: list = None) -> dict:
    """
    Full RAG pipeline: raw query → rewrite → hybrid search → LLM → answer.
    Greetings are short-circuited — no retrieval, no LLM cost, no sources shown.
    """
    if history is None:
        history = []

    error = {"message": None, "type": None}

    # Short-circuit: greetings — let the LLM respond warmly via prompt rule 6,
    # but skip retrieval so no sources are attached.
    if _is_greeting(query):
        greeting_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context="",
            question=query,
        )
        greeting_response = llm.invoke([{"role": "user", "content": greeting_prompt}])
        return {
            "query": query,
            "rewritten_query": query,
            "answer": greeting_response.content.strip(),
            "retrieval": {"documents": [], "avg_similarity_score": 0.0},
            "is_greeting": True,
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
            "is_greeting": False,
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
            "is_greeting": False,
            "retrieval": {"documents": [], "avg_similarity_score": 0.0},
            "error": error,
        }

