"""Quick start script to test the hallucination-free engine.

This script demonstrates basic usage without requiring API keys initially.
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  HALLUCINATION-FREE LLM ENGINE - QUICK START                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Welcome to the Grammar-Constrained Hallucination-Free LLM Engine!

📋 SETUP CHECKLIST:

1. ✅ Project structure created
2. ⏳ Install dependencies: pip install -r requirements.txt
3. ⏳ Add API keys to .env file:
   - OPENAI_API_KEY (get from: https://platform.openai.com/api-keys)
   - TAVILY_API_KEY (get from: https://tavily.com/)

📚 QUICK START GUIDE:

Step 1: Install dependencies
  pip install -r requirements.txt

Step 2: Add your API keys to .env file
  Edit .env and add your OPENAI_API_KEY and TAVILY_API_KEY

Step 3: Ingest some documents
  python main.py ingest --urls https://docs.python.org/3/tutorial/

Step 4: Query the engine
  python main.py query "What is Python?"

Step 5: View statistics
  python main.py stats

🧪 TESTING:

Test schemas:
  python schemas.py

Test retriever:
  python retriever.py

Test full graph:
  python graph.py

📊 EVALUATION:

Run RAGAS evaluation (requires ingested documents):
  python -c "from evaluate import evaluate_engine, load_test_cases; from graph import build_hallucination_free_graph; from retriever import HybridRetriever; retriever = HybridRetriever(); app = build_hallucination_free_graph(retriever); test_cases = load_test_cases('test_cases.json'); evaluate_engine(test_cases, app)"

📖 DOCUMENTATION:

See README.md for detailed documentation and troubleshooting.

🎯 SUCCESS CRITERIA:

- ✅ 100% schema adherence (enforced via Pydantic)
- ✅ >90% faithfulness score (RAGAS evaluation)
- ✅ <3 second latency for simple queries
- ✅ Zero unhandled exceptions

═══════════════════════════════════════════════════════════════════════════════

Ready to build? Start with: pip install -r requirements.txt

""")
