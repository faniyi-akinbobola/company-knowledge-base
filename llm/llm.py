from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai",
    temperature=0.2,
    max_tokens=4096,
)