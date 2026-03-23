import os
import time
from urllib import response
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List,Tuple
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")

MODEL = ""
EMBEDDING_MODEL = "text-embedding-3-large"

#retrieve the vector store
def get_vector_store():
    """
    Retrieve the Chroma vector store.
    """
    vector_store = Chroma(
        embeddings=OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=3072),
        persist_directory="./data/vector_db"
    )
    return vector_store

vector_store = get_vector_store()

#create a retriever from the vector store
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

#initialize the LLM
llm = ChatOpenAI(model=MODEL, temperature=0.2)

SYSTEM_PROMPT_TEMPLATE = """
You are an internal AI assistant for ApexTech Solutions.

Answer employee questions using ONLY the provided context.

If the answer is not explicitly stated in the context, respond with:
"I could not find that information in the company documentation."

Guidelines:
- Be accurate and concise
- Do not make assumptions
- Do not add information not present in the context
- Prefer bullet points for multiple items

Context:
{context}

Question:
{question}

Answer (include source):
"""

def answer_query(query: str, history: List[Tuple[str, str]] = None) -> str:
    """
    Answer a user query using the vector store and LLM.
    """
    try:
        if history is None:
            history = []
        
        start_time = time.time()

        # Retrieve relevant documents WITH similarity scores
        docs_with_scores = vector_store.similarity_search_with_score(query)

        # Separate documents and scores
        relevant_docs = [doc for doc, score in docs_with_scores]
        scores = [score for doc, score in docs_with_scores]

        # Combine the retrieved documents into a single context string
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Tracking sources WITH similarity scores
        sources = []
        for i, (doc, score) in enumerate(docs_with_scores):
            source_name = doc.metadata.get('source', 'Unknown Source')
            # Note: ChromaDB returns distance (lower = more similar)
            # Convert to percentage similarity (optional)
            similarity_pct = (1 - score) * 100 if score <= 1 else 0
            sources.append({
                "source": source_name,
                "similarity_score": round(score, 4),
                "similarity_percentage": round(similarity_pct, 2)
            })


        #format the system prompt with the context and question
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context, question=query)

        #create messages for the LLM
        messages = [
            SystemMessage(content=system_prompt)
            ]

        for user_msg, ai_msg in history:
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=ai_msg))

        #get the LLM's response
        response = llm.invoke(messages)

        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        input_cost = usage.get("input_cost", 0)
        output_cost = usage.get("output_cost", 0)
        total_cost = usage.get("total_cost", 0)

        end_time = time.time()
        latency = end_time - start_time

        return {
            "query": query,
            "answer": response.content,
            "retrieval": {
                "documents": sources,
                "similarity_scores": scores
            }, 
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            },
            "latency": latency,
            "cost": {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            },
            "feedback": {
                "helpful": None,
                "comments": None
            },
            "error": None
        }
    except Exception as e:
        # return f"An error occurred while processing your query: {str(e)}"
        latency = time.time() - start_time

        return {
            "query": query,
            "answer": None,
            "sources": [],
            "tokens": {
                "input": 0,
                "output": 0,
                "total": 0
            },
            "latency": latency,
            "cost": {
                "input_cost": 0,
                "output_cost": 0,
                "total_cost": 0
            },
            "feedback": {
                "helpful": None,
                "comments": None
            },
            "error": str(e)   
        }