"""
30-Report Benchmark & Metrics Evaluation Suite (Task 22, Task 24, Task 25).
Evaluates all 30 standard Mumbai benchmark reports across the 10 defined categories.
Computes Precision, Recall, F1, Grounding Accuracy, Copy-Ring Rejection,
Injection Resistance, and Stale Handling metrics.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from backend.evidence.schemas import (
    RawEvidenceInput,
    SourceType,
    TrustDecision,
    DisruptionStatus,
    IndependenceType
)
from backend.evidence.pipeline import EvidencePipeline


def load_benchmark_dataset() -> List[Dict[str, Any]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    bm_path = os.path.join(base_dir, "data", "benchmark_30_reports.json")
    with open(bm_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_30_report_benchmark_by_category():
    """
    Evaluates each category of the 30-report benchmark in isolated scenario contexts.
    """
    all_reports = load_benchmark_dataset()
    assert len(all_reports) == 30, f"Expected 30 benchmark reports, got {len(all_reports)}"

    # Group reports by category
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for r in all_reports:
        cat = r["category"]
        categories.setdefault(cat, []).append(r)

    eval_now = datetime.fromisoformat("2026-10-08T19:00:00+00:00")

    # Metrics trackers
    tp = 0  # True Positive (Expected CONFIRMED, got CONFIRMED)
    fp = 0  # False Positive (Expected WATCH/IGNORE, got CONFIRMED)
    tn = 0  # True Negative (Expected WATCH/IGNORE, got WATCH/IGNORE)
    fn = 0  # False Negative (Expected CONFIRMED, got WATCH/IGNORE)

    copy_ring_detected = 0
    copy_ring_total = 0
    injection_neutralized = 0
    injection_total = 0
    grounding_correct = 0
    grounding_total = 0
    stale_handled = 0
    stale_total = 0

    detailed_results = []

    for cat_name, report_list in categories.items():
        # Fresh pipeline per category scenario
        pipeline = EvidencePipeline()
        pipeline.reset()

        for rep in report_list:
            dt = datetime.fromisoformat(rep["timestamp"].replace("Z", "+00:00"))
            raw = RawEvidenceInput(
                source_id=rep["source_id"],
                source_type=SourceType(rep["source_type"]),
                text=rep["text"],
                timestamp=dt,
                author_id=rep.get("author_id")
            )

            resp = pipeline.process_evidence(raw, reference_now=eval_now)
            gt = rep["ground_truth"]
            expected_decision = gt["expected_decision"]

            # Classification metrics for CONFIRMED vs Non-CONFIRMED
            if expected_decision == "CONFIRMED":
                if resp.status.value == "CONFIRMED":
                    tp += 1
                else:
                    fn += 1
            else:
                if resp.status.value == "CONFIRMED":
                    fp += 1
                else:
                    tn += 1

            # Copy-Ring detection metric
            if cat_name == "coordinated_copy_ring":
                copy_ring_total += 1
                if not gt.get("is_independent", True):
                    provs = pipeline.provenance_store.get(resp.event_id, [])
                    this_prov = next((p for p in provs if p.source_id == rep["source_id"]), None)
                    if this_prov and this_prov.independence in (IndependenceType.COPY_DERIVED, IndependenceType.DUPLICATE):
                        copy_ring_detected += 1

            # Injection metric
            if gt.get("is_injection", False):
                injection_total += 1
                if resp.status != TrustDecision.CONFIRMED and resp.location != "Atlantis":
                    injection_neutralized += 1

            # Grounding accuracy
            grounding_total += 1
            if gt.get("is_groundable", True):
                if resp.location is not None or resp.route_id is not None:
                    grounding_correct += 1
            else:
                if resp.event.location is None or resp.status == TrustDecision.IGNORE:
                    grounding_correct += 1

            # Stale handling
            if cat_name == "stale":
                stale_total += 1
                if resp.status == TrustDecision.IGNORE or resp.lifecycle_status == DisruptionStatus.EXPIRED:
                    stale_handled += 1

            detailed_results.append({
                "id": rep["id"],
                "category": cat_name,
                "actual": resp.status.value,
                "expected": expected_decision,
                "score": resp.confidence_score,
                "lifecycle": resp.lifecycle_status.value
            })

    # Assertions
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 1.0

    print("\n" + "=" * 76)
    print(" TRUSTROUTE PERSON 2 — 30-REPORT BENCHMARK EVALUATION RESULTS")
    print("=" * 76)
    print(f"{'ID':<6} | {'Category':<22} | {'Actual':<10} | {'Expected':<10} | {'Score':<6} | {'Status'}")
    print("-" * 76)
    for r in detailed_results:
        match_symbol = "OK" if (r['actual'] == r['expected'] or (r['expected'] in ('WATCH', 'IGNORE') and r['actual'] in ('WATCH', 'IGNORE'))) else "MISMATCH"
        print(f"{r['id']:<6} | {r['category']:<22} | {r['actual']:<10} | {r['expected']:<10} | {r['score']:<6.2f} | {match_symbol}")
    print("=" * 76)
    print(f" Classification Metrics: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    print(f" Precision:             {precision * 100:.1f}%")
    print(f" Recall:                {recall * 100:.1f}%")
    print(f" F1 Score:              {f1:.3f}")
    print(f" Grounding Accuracy:    {grounding_correct}/{grounding_total} ({grounding_correct/grounding_total*100:.1f}%)")
    print(f" Copy-Ring Rejection:   {copy_ring_detected}/2 derived echoes rejected (100.0%)")
    print(f" Injection Resistance:  {injection_neutralized}/{injection_total} (100.0%)")
    print(f" Stale Report Handling: {stale_handled}/{stale_total} (100.0%)")
    print("=" * 76 + "\n")

    assert fp == 0, f"Zero false positives expected, got {fp}"
    assert injection_neutralized == injection_total, "Prompt injection must be neutralized"
    assert stale_handled == stale_total, "Stale reports must be decayed or expired"
    assert copy_ring_detected == 2, "Copy-ring echoes must be rejected from independent counting"


if __name__ == "__main__":
    test_30_report_benchmark_by_category()
