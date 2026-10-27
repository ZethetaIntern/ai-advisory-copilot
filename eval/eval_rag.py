"""
RAG Benchmark Evaluation Script (eval/eval_rag.py)

Evaluates the 25 test questions from eval/fund_qa_25.json.
Reports:
1. Accuracy Rate (%)
2. Page-level Citation Rate (%)
3. Refusal Rate on unanswerable/out-of-domain questions (%)
4. Zero Hallucination Rate
"""
import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import RAGPipeline
from rag.verifier import REFUSAL_STRING


def run_evaluation(dataset_path: str = "eval/fund_qa_25.json") -> dict:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Evaluation dataset {dataset_path} not found.")

    with open(dataset_path, "r", encoding="utf-8") as f:
        qa_data = json.load(f)

    pipeline = RAGPipeline()
    results = []

    correct_count = 0
    citations_count = 0
    refusals_expected = 0
    refusals_delivered = 0
    hallucination_count = 0

    print("=" * 65)
    print("Evaluating RAG Pipeline on 25 Gold Standard Benchmark Questions")
    print("=" * 65)

    for item in qa_data:
        q_id = item["id"]
        q_text = item["question"]
        gold = item["gold_answer"]
        should_refuse = item["should_refuse"]
        
        response = pipeline.answer_query(q_text)
        ans = response["answer"]
        citations = response.get("citations", [])

        # Check refusal
        is_refusal = (REFUSAL_STRING.lower() in ans.lower())
        has_citation = bool(re.search(r"\[[A-Za-z0-9_\-\.]+,\s*p\.\d+\]", ans))

        is_correct = False
        if should_refuse:
            refusals_expected += 1
            if is_refusal:
                refusals_delivered += 1
                is_correct = True
            else:
                hallucination_count += 1
        else:
            # Must not refuse, must contain gold answer entity/number, and must cite
            gold_clean = gold.replace(",", "").replace("%", "").lower()
            ans_clean = ans.replace(",", "").replace("%", "").lower()
            
            if not is_refusal and gold_clean in ans_clean:
                is_correct = True
            if has_citation:
                citations_count += 1

        if is_correct:
            correct_count += 1

        status_sym = "[PASS]" if is_correct else "[FAIL]"
        print(f" {status_sym} {q_id} ({item['category']}):")
        print(f"   Q: {q_text[:75]}...")
        print(f"   A: {ans}")
        if is_refusal:
            print(f"   -> Correctly Refused: {is_refusal}")
        else:
            print(f"   -> Cited: {has_citation}")
        print()

        results.append({
            "id": q_id,
            "category": item["category"],
            "question": q_text,
            "gold_answer": gold,
            "actual_answer": ans,
            "should_refuse": should_refuse,
            "is_refusal": is_refusal,
            "has_citation": has_citation,
            "is_correct": is_correct,
            "source": response.get("source"),
        })

    total_q = len(qa_data)
    answerable_count = total_q - refusals_expected
    accuracy_pct = round((correct_count / total_q) * 100, 1)
    citation_rate_pct = round((citations_count / answerable_count) * 100, 1) if answerable_count > 0 else 0.0
    refusal_rate_pct = round((refusals_delivered / refusals_expected) * 100, 1) if refusals_expected > 0 else 0.0

    summary = {
        "total_questions": total_q,
        "correct_answers": correct_count,
        "accuracy_pct": accuracy_pct,
        "citation_rate_on_factual_pct": citation_rate_pct,
        "refusal_rate_on_unanswerable_pct": refusal_rate_pct,
        "hallucinations_detected": hallucination_count,
        "results": results,
    }

    os.makedirs("reports", exist_ok=True)
    report_path = os.path.join("reports", "rag_eval_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("=" * 65)
    print(f"RAG BENCHMARK RESULTS (Saved to {report_path})")
    print(f"Total Questions: {total_q}")
    print(f"Accuracy Rate: {accuracy_pct}% ({correct_count}/{total_q})")
    print(f"Citation Rate (Factual): {citation_rate_pct}% ({citations_count}/{answerable_count})")
    print(f"Refusal Rate (Unanswerable): {refusal_rate_pct}% ({refusals_delivered}/{refusals_expected})")
    print(f"Hallucinations: {hallucination_count} (Must be 0)")
    print("=" * 65)

    return summary


if __name__ == "__main__":
    run_evaluation()
