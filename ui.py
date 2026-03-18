import chainlit as cl
import time
from answer import answer_query


@cl.on_chat_start
async def start():
    await cl.Message(
    content = """
    👋 Welcome to the ApexTech Solutions AI Assistant.

    I can help you find information from company documents such as HR policies, onboarding guides, and internal resources.

    Ask me anything about company processes, policies, or tools — and I’ll provide answers along with the relevant sources.

    If the information isn’t available in the documentation, I’ll let you know.
    """    ).send()


@cl.on_message
async def main(message: cl.Message):
    user_query = message.content

    start_time = time.time()

    # Run your RAG pipeline
    answer, sources = answer_query(user_query)

    end_time = time.time()

    answer = answer.get("answer", "")
    sources = sources.get("sources", [])
    tokens = sources.get("tokens", {})
    latency = sources.get("latency", {})

    # Main response
    msg = cl.Message(content=answer)
    await msg.send()

    # ---- Optional UI Enhancements (VERY IMPORTANT) ---- #

    # 1️⃣ Show sources (RAG transparency)
    if sources:
        sources_text = "\n\n".join(
            [f"📄 {i+1}. {src}" for i, src in enumerate(sources)]
        )
        await cl.Message(
            content=f"### 📚 Sources\n{sources_text}"
        ).send()

    # 2️⃣ Show token usage
    if tokens:
        await cl.Message(
            content=f"### 🔢 Token Usage\nInput: {tokens.get('input', 0)} | Output: {tokens.get('output', 0)}"
        ).send()

    # 3️⃣ Show latency
    total_time = end_time - start_time

    await cl.Message(
        content=f"### ⏱️ Latency\nTotal Response Time: {total_time:.2f}s"
    ).send()