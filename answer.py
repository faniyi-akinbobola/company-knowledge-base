import os
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

def answer_query(query: str, history: list[Tuple[str, str]] = None) -> str:
    """
    Answer a user query using the vector store and LLM.
    """
    if history is None:
        history = []

    #retrieve relevant documents from the vector store
    relevant_docs = retriever.invoke(query)

    #combine the retrieved documents into a single context string
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    #tracking sources for the retrieved documents
    sources = "\n".join([f"- {doc.metadata.get('source', 'Unknown Source')}" for doc in relevant_docs])

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

    return response.content, sources