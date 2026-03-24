import os
import sys
import subprocess
from answer import answer_query, vector_store
from ingest import ingest


def check_vector_store():
    """
    Check if the vector store exists and has documents.
    """
    try:
        count = vector_store._collection.count()
        print(f"📦 Vector store has {count} documents")
        return count > 0  # ✅ Actually checks document count, not just directory
    except Exception as e:
        print(f"⚠️ Vector store check failed: {str(e)}")
        return False


def run_ingest():
    """
    Run the ingestion pipeline.
    """
    print("⚙️ Vector store not found. Running ingestion pipeline first...\n")
    ingest()
    print("\nIngestion complete!\n")


def test_pipeline():
    """
    Test the RAG pipeline before launching the UI.
    """
    print("🧪 Testing RAG pipeline...\n")

    result = answer_query("What is the remote work policy?")

    if result["error"]["message"]:
        print(f"Pipeline test failed: {result['error']['message']} ({result['error']['type']})")
        return False

    print(f"✅ Answer:\n{result['answer']}\n")
    print(f"📚 Documents Retrieved: {result['retrieval']['num_documents']}")
    print(f"📊 Avg Similarity: {((2 - result['retrieval']['avg_similarity_score']) / 2) * 100:.2f}%")
    print(f"🔢 Tokens: {result['tokens']['total']}")
    print(f"💰 Cost: ${result['cost']['total_cost']:.6f}")
    print(f"⏱️ Latency: {result['latency']:.2f}s")

    return True

def run_ui():
    """
    Launch the Chainlit UI using subprocess.
    """
    print("\n🚀 Launching Chainlit UI...\n")
    subprocess.run(["chainlit", "run", "ui.py"], check=True)  # ✅ Launch as subprocess

def main():
    print("ApexTech Solutions Knowledge Base\n")

    # Step 1: Check vector store — run ingest if missing
    if not check_vector_store():
        run_ingest()

    # Step 2: Test pipeline
    pipeline_ok = test_pipeline()

    if not pipeline_ok:
        print("Pipeline test failed. Please check your setup before launching the UI.")
        sys.exit(1)

    # Step 3: Launch UI
    run_ui()

if __name__ == "__main__":
    main()
