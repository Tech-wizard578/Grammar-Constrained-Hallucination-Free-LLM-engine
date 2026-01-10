# Grammar-Constrained Hallucination-Free LLM Engine

A production-grade LLM engine that enforces structured outputs and eliminates hallucinations through grammar-constrained generation, RAG, and self-verification.

## 🎯 Features

- **Zero Hallucinations**: Self-verifying RAG pipeline with CRAG and Self-RAG techniques
- **Structured Outputs**: 100% schema adherence using Pydantic + Instructor
- **Agentic Workflow**: LangGraph orchestration with conditional routing
- **Web Search Fallback**: Automatic Tavily search when KB insufficient
- **RAGAS Evaluation**: Measure faithfulness, answer relevancy, and context precision

## 📋 Requirements

- Python 3.10+
- OpenAI API key
- Tavily API key (for web search)

## 🚀 Installation

1. **Clone/Navigate to project directory**:
```bash
cd hallucination_free_engine
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy template
cp .env.template .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-proj-...
# TAVILY_API_KEY=tvly-...
```

## 💡 Usage

### 1. Ingest Documents

```bash
# From URLs
python main.py ingest --urls https://docs.python.org/3/tutorial/ https://en.wikipedia.org/wiki/RAG

# From files
python main.py ingest --files document.pdf article.txt

# Both
python main.py ingest --urls https://example.com --files doc.pdf
```

### 2. Query the Engine

```bash
python main.py query "What is retrieval-augmented generation?"
```

**Example Output**:
```
🧠 Hallucination-Free LLM Engine
Grammar-Constrained RAG with Self-Verification

❓ Query: What is retrieval-augmented generation?

╭─ Answer ─────────────────────────────────────────╮
│ Retrieval-augmented generation (RAG) is a       │
│ technique that combines information retrieval   │
│ with text generation to produce factual answers. │
╰──────────────────────────────────────────────────╯

Confidence: High

Reasoning:
Based on Source 0 which states "RAG combines retrieval and generation",
we can conclude that it's a hybrid approach...

Citations:
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Source   ┃ Quote                        ┃ Relevance ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 0        │ RAG combines retrieval...    │ 0.95      │
└──────────┴──────────────────────────────┴───────────┘
```

### 3. View Statistics

```bash
python main.py stats
```

### 4. Clear Knowledge Base

```bash
python main.py clear --confirm
```

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────┐
│  RETRIEVE   │ ← Vector DB (ChromaDB)
└──────┬──────┘
       ↓
┌─────────────┐
│ GRADE DOCS  │ ← CRAG filtering
└──────┬──────┘
       ↓
   All irrelevant?
   ├─ Yes → WEB SEARCH (Tavily)
   └─ No  → GENERATE
              ↓
       ┌──────────────┐
       │   GENERATE   │ ← GPT-4o + Instructor
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │    VERIFY    │ ← Self-RAG
       └──────┬───────┘
              ↓
       Hallucination?
       ├─ Yes → Re-retrieve (max 3x)
       └─ No  → OUTPUT
```

## 📊 Evaluation

Run RAGAS evaluation:

```python
from evaluate import evaluate_engine
from graph import build_hallucination_free_graph
from retriever import HybridRetriever

retriever = HybridRetriever()
app = build_hallucination_free_graph(retriever)

test_cases = [
    {"question": "What is Python?", "expected_answer": "A programming language"},
    # Add more test cases...
]

scores = evaluate_engine(test_cases, app)
```

**Target Scores**:
- Faithfulness: >0.90
- Answer Relevancy: >0.80
- Context Precision: >0.70

## 🔧 Configuration

Edit `.env` to customize:

```bash
# Models
DEFAULT_MODEL=gpt-4o-mini        # Fast model for routing
SMART_MODEL=gpt-4o               # Smart model for generation
EMBEDDING_MODEL=text-embedding-3-small

# Retrieval
CHUNK_SIZE=500                   # Token chunk size
CHUNK_OVERLAP=50                 # Overlap between chunks
TOP_K_RETRIEVAL=5                # Number of docs to retrieve

# Workflow
MAX_RETRIES=3                    # Max retries for LLM calls
ITERATION_LIMIT=3                # Max iterations for hallucination correction
```

## 📁 Project Structure

```
hallucination_free_engine/
├── config.py          # Configuration management
├── schemas.py         # Pydantic models for structured outputs
├── retriever.py       # ChromaDB RAG pipeline
├── agents.py          # LangGraph nodes
├── graph.py           # Workflow orchestration
├── evaluate.py        # RAGAS evaluation
├── main.py            # CLI interface
├── requirements.txt   # Dependencies
├── .env.template      # Environment template
└── README.md          # This file
```

## 🧪 Testing

Test individual components:

```bash
# Test schemas
python schemas.py

# Test retriever
python retriever.py

# Test full graph
python graph.py
```

## ⚠️ Known Limitations

1. **Cost**: Uses GPT-4o (~$0.01-0.05 per query)
2. **Latency**: 3-10 seconds per query depending on complexity
3. **Context Window**: Limited to 500 token chunks (configurable)
4. **Web Search**: Requires Tavily API (3 free searches/day on free tier)

## 🐛 Troubleshooting

### "No documents retrieved"
- Check if documents were ingested: `python main.py stats`
- Try broader query terms
- Engine will fallback to web search automatically

### "ValidationError on schema"
- This indicates LLM output doesn't match schema
- Usually auto-corrected by Instructor's retry mechanism
- Check system prompt in `agents.py` if persistent

### "Rate limit error"
- Reduce query frequency
- Use cheaper model: `DEFAULT_MODEL=gpt-3.5-turbo`

### "Faithfulness score < 0.9"
- Strengthen system prompt in `agents.py`
- Increase `CHUNK_SIZE` for more context
- Add more verification questions

## 📚 References

- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Instructor](https://python.useinstructor.com/)
- [RAGAS](https://docs.ragas.io/)
- [ChromaDB](https://www.trychroma.com/)

## 📄 License

MIT License - feel free to use for academic or commercial projects.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ using LangChain, LangGraph, and Instructor**
