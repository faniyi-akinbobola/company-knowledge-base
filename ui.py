import chainlit as cl
from answer import answer_query


@cl.on_chat_start
async def start():
    await cl.Message(
    content = """
     Welcome to the ApexTech Solutions AI Assistant.

    I can help you find information from company documents such as HR policies, onboarding guides, and internal resources.

    Ask me anything about company processes, policies, or tools — and I’ll provide answers along with the relevant sources.

    If the information isn’t available in the documentation, I’ll let you know.
    """    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    user_query = message.content
     # Get conversation history
    history = cl.user_session.get("history")

    try:
        # Run RAG pipeline with history
        result = answer_query(user_query, history=history)
    except Exception as e:
        await cl.Message(content=f" Error: {str(e)}").send()
        return

    # Update history
    history.append((user_query, result["answer"]))
    cl.user_session.set("history", history)

    # Send main answer
    await cl.Message(content=result["answer"]).send()

    # Show sources
    if result["sources"]:
        sources_text = "\n".join(
            [f"📄 {i+1}. {src}" for i, src in enumerate(result["sources"])]
        )
        await cl.Message(content=f"### 📚 Sources\n{sources_text}").send()

        # Show sources WITH similarity scores
    if result["retrieval"]["documents"]:
        sources_text = "### 📚 Retrieved Documents\n\n"
        for i, doc in enumerate(result["retrieval"]["documents"], 1):
            sources_text += f"**{i}. {doc['source']}**\n"
            sources_text += f"   - Similarity: {doc['similarity_percentage']:.2f}%\n"
            sources_text += f"   - Distance: {doc['similarity_score']:.4f}\n\n"
        
        sources_text += f"**Average Similarity:** {(1 - result['retrieval']['avg_similarity']) * 100:.2f}%"
        await cl.Message(content=sources_text).send()

    # Show token usage
    tokens = result["tokens"]
    await cl.Message(
        content=f"### Token Usage\n"
                f"Input: {tokens['input']} | Output: {tokens['output']} | Total: {tokens['total']}"
    ).send()

    # Show latency
    await cl.Message(
        content=f"### ⏱Latency\nTotal Response Time: {result['latency']:.2f}s"
    ).send()

    # start_time = time.time()

    # # Run your RAG pipeline
    # answer, sources = answer_query(user_query)

    # end_time = time.time()

    # tokens = sources.get("tokens", {})
    # latency = sources.get("latency", {})

    # # Main response
    # msg = cl.Message(content=answer)
    # await msg.send()

    # # ---- Optional UI Enhancements (VERY IMPORTANT) ---- #

    # # 1️⃣ Show sources (RAG transparency)
    # if sources:
    #     sources_text = "\n\n".join(
    #         [f"📄 {i+1}. {src}" for i, src in enumerate(sources)]
    #     )
    #     await cl.Message(
    #         content=f"### 📚 Sources\n{sources_text}"
    #     ).send()

    # # 2️⃣ Show token usage
    # if tokens:
    #     await cl.Message(
    #         content=f"### 🔢 Token Usage\nInput: {tokens.get('input', 0)} | Output: {tokens.get('output', 0)}"
    #     ).send()

    # # 3️⃣ Show latency
    # total_time = end_time - start_time

    # await cl.Message(
    #     content=f"### ⏱️ Latency\nTotal Response Time: {total_time:.2f}s"
    # ).send()