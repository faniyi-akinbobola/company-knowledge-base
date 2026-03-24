import os
import time
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List,Tuple
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")

MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_per_1k": 0.00015,
        "output_per_1k": 0.0006
    },
    "gpt-4o": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.015
    }
}

#retrieve the vector store
def get_vector_store():
    """
    Retrieve the Chroma vector store.
    """
    vector_store = Chroma(
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=1536),
        persist_directory="./data/vector_db"
    )
    return vector_store

vector_store = get_vector_store()

#create a retriever from the vector store
# retriever = vector_store.as_retriever(search_kwargs={"k": 3})

#initialize the LLM
llm = ChatOpenAI(model=MODEL, temperature=0.2)

SYSTEM_PROMPT_TEMPLATE = """
You are an internal AI assistant for ApexTech Solutions.

Answer employee questions using ONLY the provided context.

If the answer is not explicitly stated in the context but can be reasonably 
inferred from it, provide the inferred answer and indicate it is inferred.

If the answer cannot be found or inferred from the context at all, respond with:
"I could not find that information in the company documentation."

Guidelines:
- Be accurate and concise
- Prefer bullet points for multiple items
- If referencing a contact or department, include their details if available
- Do not add information not present in the context

Context:
{context}

Question:
{question}

Answer (include source):
"""

def answer_query(query: str, history: List[Tuple[str, str]] = None) -> dict:
    """
    Answer a user query using the vector store and LLM.
    """
    start_time = time.time()
    try:
        if history is None:
            history = []
        
        # Retrieve relevant documents WITH similarity scores
        docs_with_scores = vector_store.similarity_search_with_score(query, k=5)

        # Combine the retrieved documents into a single context string
        context = "\n\n".join([doc.page_content for doc, score in docs_with_scores])

        #format the system prompt with the context and question
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context, question=query)

        #create messages for the LLM
        messages = [
            SystemMessage(content=system_prompt)
        ]

        for user_msg, ai_msg in history:
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=ai_msg))
        
        messages.append(HumanMessage(content=query))

        #get the LLM's response
        response = llm.invoke(messages)

        #Extracting token usage
        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
        input_tokens = usage.get("input_tokens", 0)  if isinstance(usage, dict) else getattr(usage, "input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)  if isinstance(usage, dict) else getattr(usage, "output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)  if isinstance(usage, dict) else getattr(usage, "total_tokens", 0)

        #Cost calculation using MODEL_PRICING and token counts
        pricing = MODEL_PRICING.get(MODEL, {"input_per_1k": 0, "output_per_1k": 0})
        input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_per_1k"]
        total_cost = input_cost + output_cost

        end_time = time.time()
        latency = end_time - start_time

        return {
            "query": query,
            "answer": response.content,
            "model": MODEL,
            "retrieval": {
                "documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": round(score, 4),
                        "similarity_percentage": round((((2 - score) / 2) * 100), 2) 
                    } for doc, score in docs_with_scores
                ],
                "num_documents": len(docs_with_scores),
                "avg_similarity_score": round(sum(score for _, score in docs_with_scores) / len(docs_with_scores), 4) if docs_with_scores else 0
            }, 
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            },
            "context": context,
            "latency": latency,
            "cost": {
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
                "total_cost": round(total_cost, 6)
            },
            "feedback": {
                "rating": None,   # upvote/downvote or 1–5
                "comment": None
            },
            "error": {
                "message": None,
                "type": None
            }
        }
    except Exception as e:
        latency = time.time() - start_time

        return {
            "query": query,
            "answer": None,
            "model": MODEL,
            "retrieval": {           
                "documents": [],
                "num_documents": 0,
                "avg_similarity_score": 0
            },
            "context": None,
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
                "rating": None,   # upvote/downvote or 1–5
                "comment": None
            },
            "error": {
                "message": str(e),
                "type": type(e).__name__
            } 
        }