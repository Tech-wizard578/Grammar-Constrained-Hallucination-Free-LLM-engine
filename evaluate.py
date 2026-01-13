"""RAGAS evaluation module for measuring hallucination-free engine performance.

Evaluates the engine on:
- Faithfulness: Are answers grounded in retrieved context?
- Answer Relevancy: Do answers address the query?
- Context Precision: Are retrieved docs relevant?
"""

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from typing import List, Dict, Any
from datetime import datetime
import json
from config import get_config_summary


def evaluate_engine(test_cases: List[dict], app, verbose: bool = True) -> Dict[str, Any]:
    """Run RAGAS evaluation on test queries.
    
    Args:
        test_cases: List of dicts with keys: question, expected_answer (optional)
        app: Compiled LangGraph application
        verbose: Whether to print detailed results
        
    Returns:
        Dictionary with RAGAS scores, timestamp, and metadata
        
    Example test_case:
        {
            "question": "What is Python?",
            "expected_answer": "A programming language"  # Optional
        }
    """
    eval_timestamp = datetime.now().isoformat()
    
    print("\n" + "="*80)
    print(f"📊 RAGAS EVALUATION (started: {eval_timestamp})")
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
        
        return {
            "timestamp": eval_timestamp,
            "scores": dict(scores),
            "num_test_cases": len(test_cases),
            "config": get_config_summary(),
            "targets_met": targets_met
        }
        
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


def compare_with_baseline(current_results: dict, baseline_path: str) -> Dict[str, Any]:
    """Compare current evaluation scores with a baseline.
    
    Args:
        current_results: Current evaluation results dictionary
        baseline_path: Path to baseline JSON file
        
    Returns:
        Dictionary with improvements/regressions for each metric
    """
    try:
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)
        
        current_scores = current_results.get("scores", {})
        baseline_scores = baseline.get("scores", {})
        
        comparison = {
            "baseline_timestamp": baseline.get("timestamp", "unknown"),
            "current_timestamp": current_results.get("timestamp", "unknown"),
            "improvements": {},
            "overall_improved": True
        }
        
        for metric in current_scores:
            if metric in baseline_scores:
                diff = current_scores[metric] - baseline_scores[metric]
                comparison["improvements"][metric] = {
                    "baseline": round(baseline_scores[metric], 3),
                    "current": round(current_scores[metric], 3),
                    "change": round(diff, 3),
                    "improved": diff >= 0
                }
                if diff < 0:
                    comparison["overall_improved"] = False
        
        # Print comparison summary
        print("\n" + "="*60)
        print("📊 BASELINE COMPARISON")
        print("="*60)
        for metric, data in comparison["improvements"].items():
            arrow = "⬆️" if data["improved"] else "⬇️"
            print(f"  {metric}: {data['baseline']:.3f} → {data['current']:.3f} ({data['change']:+.3f}) {arrow}")
        print("="*60)
        
        return comparison
        
    except FileNotFoundError:
        print(f"⚠️ Baseline file not found: {baseline_path}")
        return {"error": f"Baseline not found: {baseline_path}"}
    except Exception as e:
        print(f"❌ Error comparing with baseline: {e}")
        return {"error": str(e)}


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
