import os
import sys
import logging

# Ensure project root is on sys.path when running via `chainlit run UI/ui.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress noisy third-party loggers
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import chainlit as cl
from rag.answer import answer_query
from dotenv import load_dotenv

load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content=(
            "👋 Welcome to the **ApexTech Solutions AI Assistant**.\n\n"
            "Ask me anything about company policies, processes, or internal resources — "
            "I'll provide answers with relevant sources.\n"
            "If the information isn't available in the documentation, I'll let you know."
        )
    ).send()

def clean_source_name(source: str) -> str:
    """Remove path and extension, return human-readable name."""
    filename = os.path.basename(source)
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ")
    return name.title()

@cl.on_message
async def handle_message(message: cl.Message):
    user_query = message.content
    history = cl.user_session.get("history", [])

    try:
        result = await cl.make_async(answer_query)(user_query, history=history)
    except Exception as e:
        await cl.Message(content=f" An error occurred: {str(e)}").send()
        return

    if result["error"]["message"]:
        await cl.Message(content=f" {result['error']['message']}").send()
        return

    # ✅ Update history
    history.append((user_query, result["answer"]))
    cl.user_session.set("history", history)

    # ✅ Send answer
    await cl.Message(content=result["answer"]).send()

    # ✅ Only show sources if answer was found in docs
    not_found = "i could not find" in result["answer"].lower()

    if not not_found and result["retrieval"]["documents"]:
        seen = set()
        unique_sources = []
        for doc in result["retrieval"]["documents"]:
            source = doc["metadata"].get("source", "Unknown")
            clean = clean_source_name(source)
            if clean not in seen:
                seen.add(clean)
                unique_sources.append(clean)

        if unique_sources:
            sources_text = "### 📚 Sources\n"
            for i, source in enumerate(unique_sources, 1):
                sources_text += f"{i}. {source}\n"
            await cl.Message(content=sources_text).send()