import os
import chainlit as cl
from answer import answer_query

def classify_query(query: str) -> str:
    q = query.lower().strip()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings", "what's up", "yo", "hi there", "hello there", "hey there", "hi!", "hello!", "hey!",]

    if q in greetings:
        return "greeting"

    return "rag"

def clean_source_name(source: str) -> str:
    """Remove path and extension from source name."""
    filename = os.path.basename(source)                    # e.g. security_policy.md
    name = os.path.splitext(filename)[0]                   # e.g. security_policy
    name = name.replace("_", " ").replace("-", " ")        # e.g. security policy
    return name.title()  

@cl.set_chat_profiles
async def set_chat_profiles():
    return [
        cl.ChatProfile(
            name="User",
            markdown_description="**Standard Mode** — Clean responses with sources only.",
            icon="👤"
        ),
        cl.ChatProfile(
            name="Developer",
            markdown_description="**Developer Mode** — Full metrics including tokens, cost, latency, and similarity scores.",
            icon="🛠️"
        )
    ]

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])

    profile = cl.user_session.get("chat_profile")

    if profile == "Developer":
        await cl.Message(
            content="""
                    🛠️ **Developer Mode Active**

                    You have access to full pipeline metrics including:
                    - Token usage and cost
                    - Latency
                    - Retrieved documents and similarity scores

                    Ask me anything!
                """
        ).send()
    else:
        await cl.Message(
            content="""
👋 Welcome to the **ApexTech Solutions AI Assistant**.

Ask me anything about company policies, processes, or internal resources — I'll provide answers with relevant sources.If the information isn't available in the documentation, I'll let you know.
                """
        ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    user_query = message.content

    # NEW: classify query BEFORE running RAG
    route = classify_query(user_query)

    if route == "greeting":
        await cl.Message(
            content="Hi! What would you like to know about ApexTech’s policies or resources?"
        ).send()
        return

    
     # Get conversation history
    history = cl.user_session.get("history", [])
    profile = cl.user_session.get("chat_profile")

    try:
        # Run RAG pipeline with history
        result = answer_query(user_query, history=history)
    except Exception as e:
        await cl.Message(content=f" Error: {str(e)}").send()
        return
    
    # Check error FIRST
    if result["error"]["message"]:
        await cl.Message(content=f" Error: {result['error']['message']}").send()
        return

    # Update history
    history.append((user_query, result["answer"]))
    cl.user_session.set("history", history)

    # Send main answer
    await cl.Message(content=result["answer"]).send()

    #  Only show sources if answer was actually found in docs
    not_found = "i could not find" in result["answer"].lower()

    if not not_found and result["retrieval"]["documents"]:

        #  Deduplicate sources
        seen = set()
        unique_sources = []
        for doc in result["retrieval"]["documents"]:
            source = doc["metadata"].get("source", "Unknown")
            clean = clean_source_name(source)
            if clean not in seen:
                seen.add(clean)
                unique_sources.append(clean)


    #  User mode — clean sources only (no scores)
    if profile == "User":
        if result["retrieval"]["documents"]:
            sources_text = "### Sources\n"
            for i, source_name in enumerate(unique_sources, 1):
                sources_text += f"{i}. `{source_name}`\n"
            await cl.Message(content=sources_text).send()

    # Developer mode only — full metrics
    if profile == "Developer":

        docs_text = "### 🔍 Retrieved Documents\n\n"
        for i, doc in enumerate(result["retrieval"]["documents"], 1):
            source_name = doc["metadata"].get("source", "Unknown")
            docs_text += f"**{i}. {source_name}**\n"
            docs_text += f"   - Similarity: `{doc['similarity_percentage']:.2f}%`\n"
            docs_text += f"   - Distance Score: `{doc['similarity_score']:.4f}`\n\n"

        avg_similarity = ((2 - result['retrieval']['avg_similarity_score']) / 2) * 100
        docs_text += f"**Average Similarity:** `{avg_similarity:.2f}%`"
        await cl.Message(content=docs_text).send()

        # Show token usage
        tokens = result["tokens"]
        await cl.Message(
            content=f"### Token Usage\n"
                    f"Input: {tokens['input']} | Output: {tokens['output']} | Total: {tokens['total']}"
        ).send()

        #show cost usage
        cost = result["cost"]
        await cl.Message(
            content=f"###  Cost\nInput: ${cost['input_cost']:.6f} | Output: ${cost['output_cost']:.6f} | Total: ${cost['total_cost']:.6f}"
        ).send()

        # Show latency
        await cl.Message(
            content=f"###  Latency\nTotal Response Time: {result['latency']:.2f}s"
        ).send()

        # Show error if present
        if result["error"]["message"]:
            await cl.Message(
                content=f"###  Error\n{result['error']['message']} (Type: {result['error']['type']})"
        ).send()
    