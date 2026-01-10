"""RAGAS evaluation module for measuring hallucination-free engine performance.

Evaluates the engine on:
- Faithfulness: Are answers grounded in retrieved context?
- Answer Relevancy: Do answers address the query?
- Context Precision: Are retrieved docs relevant?
"""

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from typing import List, Dict
import json


def evaluate_engine(test_cases: List[dict], app, verbose: bool = True) -> dict:
    """Run RAGAS evaluation on test queries.
    
    Args:
        test_cases: List of dicts with keys: question, expected_answer (optional)
        app: Compiled LangGraph application
        verbose: Whether to print detailed results
        
    Returns:
        Dictionary with RAGAS scores
        
    Example test_case:
        {
            "question": "What is Python?",
            "expected_answer": "A programming language"  # Optional
        }
    """
    print("\n" + "="*80)
    print("📊 RAGAS EVALUATION")
    print("="*80)
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Evaluating: {case['question'][:60]}...")
        
        # Run engine
        try:
            output = app.invoke({
                "question": case["question"],
                "documents": [],
                "generation": None,
                "web_search_needed": False,
                "iteration_count": 0,
                "errors": []
            })
            
            generation = output.get("generation")
            documents = output.get("documents", [])
            
            if generation:
                results.append({
                    "question": case["question"],
                    "answer": generation.answer,
                    "contexts": [doc["content"] for doc in documents],
                    "ground_truth": case.get("expected_answer", "")
                })
                print(f"  ✅ Answer: {generation.answer[:80]}...")
            else:
                print(f"  ❌ No generation produced")
                # Add placeholder for failed queries
                results.append({
                    "question": case["question"],
                    "answer": "No answer generated",
                    "contexts": ["No context"],
                    "ground_truth": case.get("expected_answer", "")
                })
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "question": case["question"],
                "answer": f"Error: {e}",
                "contexts": ["Error"],
                "ground_truth": case.get("expected_answer", "")
            })
    
    # Convert to RAGAS dataset
    print("\n" + "="*80)
    print("🔬 Computing RAGAS Metrics...")
    print("="*80)
    
    dataset = Dataset.from_list(results)
    
    # Evaluate (only use metrics that don't require ground_truth if not provided)
    metrics_to_use = [faithfulness, answer_relevancy, context_precision]
    
    try:
        scores = evaluate(
            dataset,
            metrics=metrics_to_use
        )
        
        print("\n📊 RAGAS Evaluation Results:")
        print("="*80)
        print(f"  Faithfulness:       {scores['faithfulness']:.3f} (target: >0.90)")
        print(f"  Answer Relevancy:   {scores['answer_relevancy']:.3f} (target: >0.80)")
        print(f"  Context Precision:  {scores['context_precision']:.3f} (target: >0.70)")
        print("="*80)
        
        # Check if targets met
        targets_met = (
            scores['faithfulness'] >= 0.90 and
            scores['answer_relevancy'] >= 0.80 and
            scores['context_precision'] >= 0.70
        )
        
        if targets_met:
            print("✅ All target scores met!")
        else:
            print("⚠️ Some targets not met - consider:")
            if scores['faithfulness'] < 0.90:
                print("  - Strengthen system prompt to enforce citations")
                print("  - Add more verification questions")
            if scores['answer_relevancy'] < 0.80:
                print("  - Improve query understanding")
                print("  - Add query decomposition")
            if scores['context_precision'] < 0.70:
                print("  - Improve document grading")
                print("  - Increase chunk size for more context")
        
        return dict(scores)
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return {}


def load_test_cases(file_path: str) -> List[dict]:
    """Load test cases from JSON file.
    
    Args:
        file_path: Path to JSON file with test cases
        
    Returns:
        List of test case dictionaries
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_evaluation_results(results: dict, output_path: str):
    """Save evaluation results to JSON file.
    
    Args:
        results: RAGAS scores dictionary
        output_path: Path to save results
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Results saved to {output_path}")


if __name__ == "__main__":
    """Run evaluation with sample test cases."""
    print("To run evaluation, you need:")
    print("1. A knowledge base with indexed documents")
    print("2. Test cases with questions and expected answers")
    print("\nExample test cases:")
    
    sample_test_cases = [
        {
            "question": "What is retrieval-augmented generation?",
            "expected_answer": "A technique that combines retrieval and generation"
        },
        {
            "question": "What is Python?",
            "expected_answer": "A high-level programming language"
        },
        {
            "question": "How do I define a function in Python?",
            "expected_answer": "Use the def keyword"
        }
    ]
    
    print(json.dumps(sample_test_cases, indent=2))
    
    print("\n\nTo run evaluation:")
    print("1. Create test_cases.json with your test cases")
    print("2. Run: python evaluate.py")
