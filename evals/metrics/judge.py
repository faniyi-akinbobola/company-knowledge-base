"""
Shared LLM judge utility for all eval metrics.

Uses a strict 1–5 rubric so scores are spread realistically across the scale,
rather than the trivially-inflated 0–1 floats that GPT tends to push toward 1.0.

Rubric (applied to every evaluation):
  5 — Excellent: fully correct, grounded, complete, no hallucinations
  4 — Good: mostly correct with minor gaps or slight imprecision
  3 — Acceptable: partially correct but missing important details or slightly off
  2 — Poor: significant errors, missing key facts, or partially hallucinated
  1 — Unacceptable: wrong, hallucinated, or completely off-topic

The raw 1–5 integer is normalised to 0.0–1.0 before being returned so downstream
code doesn't have to change.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

_JUDGE_SYSTEM = """You are a strict, impartial evaluator for an internal company knowledge-base RAG system.

Score the response using this exact 1–5 rubric:

  5 — Excellent  : Every claim is supported by the provided context. No hallucinations. 
                   All key information is present. Answer is clear and directly addresses the question.
  4 — Good       : Mostly correct and grounded. At most one minor gap or slight imprecision.
                   No harmful hallucinations.
  3 — Acceptable : Partially correct. Missing at least one important detail OR
                   contains a minor claim that cannot be verified from the context.
  2 — Poor       : Significant factual errors OR multiple key facts missing OR
                   contains information not supported by the context (hallucination).
  1 — Fail       : Wrong, completely hallucinated, off-topic, or refused a valid question.

Be strict. A "1.0" in a previous system should now be a 4 or 5 only if genuinely excellent.
Respond with ONLY a single integer: 1, 2, 3, 4, or 5. No explanation."""


def judge(prompt: str) -> float:
    """
    Score a prompt using the strict 1–5 rubric.
    Returns a float in [0.0, 1.0] (normalised from the 1–5 integer).
    Falls back to 0.0 on parse error.
    """
    judge_llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        temperature=0,
    )
    messages = [
        SystemMessage(content=_JUDGE_SYSTEM),
        HumanMessage(content=prompt),
    ]
    response = judge_llm.invoke(messages)
    try:
        raw = int(response.content.strip())
        raw = max(1, min(5, raw))          # clamp to [1, 5]
        return round((raw - 1) / 4, 4)    # normalise: 1→0.0, 3→0.5, 5→1.0
    except (ValueError, TypeError):
        return 0.0
