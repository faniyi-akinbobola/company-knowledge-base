import subprocess
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Suppress noisy third-party loggers — only show warnings/errors
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from rag.answer import answer_query
from rag.vectorstore import load_vectorstore
from rag.ingest import ingest


def check_vector_store() -> bool:
    """Check if the vector store exists and has documents."""
    try:
        vs = load_vectorstore()
        count = vs._collection.count()
        if count == 0:
            print("  Vector store is empty.")
            return False
        print(f" Vector store loaded — {count} chunks found.")
        return True
    except Exception as e:
        print(f" Vector store check failed: {e}")
        return False


def run_ingest():
    """Run the ingestion pipeline."""
    print("🔄 Running ingestion pipeline...")
    try:
        ingest()
        print(" Ingestion complete.")
    except Exception as e:
        print(f" Ingestion failed: {e}")
        sys.exit(1)


def test_pipeline():
    """Smoke-test the RAG pipeline."""
    print("\n🧪 Testing RAG pipeline...")
    test_query = "What is the remote work policy?"
    try:
        result = answer_query(test_query)
        print(f" Test query: {test_query}")
        print(f"   Answer preview: {result['answer'][:120]}...")
        if result["error"]["message"]:
            print(f" Pipeline error: {result['error']['message']}")
    except Exception as e:
        print(f" Pipeline test failed: {e}")
        sys.exit(1)


def run_ui():
    """Launch the Chainlit UI."""
    print("\n🚀 Launching Chainlit UI...")
    subprocess.run(
        ["chainlit", "run", "UI/ui.py", "--port", "8000"],
        check=True
    )


def main():
    print("🏢 ApexTech Solutions — Knowledge Base\n")

    if not check_vector_store():
        print(" Vector store not found — running ingestion...")
        run_ingest()

    # test_pipeline()
    run_ui()


if __name__ == "__main__":
    main()