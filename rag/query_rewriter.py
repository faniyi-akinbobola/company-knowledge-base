"""
Query Rewriter
==============
Rewrites a raw user query into a cleaner, more specific search query before
retrieval. This helps with:

- Vague queries   : "tell me about policies" → specific HR/IT/expense policy questions
- Conversational  : "what about the expenses?" (with history) → standalone question
- Abbreviations   : "WFH rules" → "remote work policy requirements"

The rewriter uses a fast, cheap LLM call (gpt-4o-mini) so latency impact is minimal.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Tuple

load_dotenv()

_rewriter_llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    temperature=0,
)

_REWRITE_SYSTEM = """You are a search query optimizer for an internal company knowledge base.

Your job: rewrite the user's question into the single best search query to retrieve 
relevant documents from the knowledge base.

Rules:
- Output ONLY the rewritten query — no explanation, no preamble, no quotes
- Make the query specific and self-contained (no pronouns like "it" or "that")
- Expand abbreviations (WFH → remote work, PTO → paid time off)
- If the question is already clear and specific, return it unchanged
- If conversation history is provided, incorporate the context to make the query standalone
- Keep the query under 20 words
"""


def rewrite_query(query: str, history: List[Tuple[str, str]] = None) -> str:
    """
    Rewrite a user query into an optimised retrieval query.

    Args:
        query:   The raw user question.
        history: List of (user_msg, ai_msg) tuples for conversation context.

    Returns:
        A rewritten query string. Falls back to the original on any error.
    """
    history = history or []

    # Build the prompt with optional conversation context
    history_text = ""
    if history:
        recent = history[-3:]  # only last 3 turns to keep prompt tight
        history_text = "\n".join(
            f"User: {u}\nAssistant: {a}" for u, a in recent
        )
        history_text = f"\nConversation so far:\n{history_text}\n"

    user_content = (
        f"{history_text}\n"
        f"User's question: {query}\n\n"
        "Rewritten search query:"
    )

    try:
        response = _rewriter_llm.invoke([
            SystemMessage(content=_REWRITE_SYSTEM),
            HumanMessage(content=user_content),
        ])
        rewritten = response.content.strip().strip('"').strip("'")
        return rewritten if rewritten else query
    except Exception:
        return query  # safe fallback — never break the pipeline
