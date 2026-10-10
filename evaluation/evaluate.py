"""
Main CLI execution script for TrustRoute Evaluation (Task 12 & 13).
Generates benchmark results, compares Baseline A, Baseline B, and TrustRoute,
and outputs formatted markdown report.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from evaluation.evaluator import TrustRouteEvaluator
from evaluation.reproducibility import ReproducibilityAuditor


def run_full_evaluation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 80)
    print("      TRUSTROUTE COMPREHENSIVE BENCHMARK & SYSTEM EVALUATION")
    print("=" * 80)

    # 1. Audit Fingerprint
    auditor = ReproducibilityAuditor(base_dir)
    audit_file = auditor.save_audit_log()
    print(f"[*] Reproducibility signature recorded to: {audit_file}")

    # 2. Evidence Engine Evaluation
    evaluator = TrustRouteEvaluator(base_dir)
    ev_res = evaluator.run_evidence_benchmark()
    print(f"\n[+] Evidence Benchmark (30 Standard Reports across 11 categories):")
    print(f"    - Precision: {ev_res['precision']*100:.2f}%")
    print(f"    - Recall:    {ev_res['recall']*100:.2f}%")
    print(f"    - F1 Score:  {ev_res['f1_score']:.4f}")
    print(f"    - FPR:       {ev_res['false_positive_rate']*100:.2f}%")
    print(f"    - FNR:       {ev_res['false_negative_rate']*100:.2f}%")
    print(f"    - Copy-Ring Rejection: {ev_res['copy_ring_rejection_rate']*100:.1f}%")
    print(f"    - Avg Latency:         {ev_res['average_latency_ms']} ms")

    # 3. Comparative Simulation Evaluation
    comp_res = evaluator.run_comparative_benchmark()
    comp = comp_res["comparison"]
    print(f"\n[+] Comparative Benchmark (30 Held-out Transit Disruption Scenarios):")
    print(f"{'Metric':<32} | {'Baseline A (Static)':<20} | {'Baseline B (Raw Crowd)':<22} | {'TrustRoute (Full)':<20}")
    print("-" * 105)
    print(f"{'Journey Success Rate (%)':<32} | {comp['Baseline_A_Static']['success_rate']*100:<20.1f} | {comp['Baseline_B_RawCrowd']['success_rate']*100:<22.1f} | {comp['TrustRoute_Proposed']['success_rate']*100:<20.1f}")
    print(f"{'Deadline Miss Rate (%)':<32} | {comp['Baseline_A_Static']['deadline_miss_rate']*100:<20.1f} | {comp['Baseline_B_RawCrowd']['deadline_miss_rate']*100:<22.1f} | {comp['TrustRoute_Proposed']['deadline_miss_rate']*100:<20.1f}")
    print(f"{'Unnecessary Reroutes (%)':<32} | {comp['Baseline_A_Static']['unnecessary_reroutes']*100:<20.1f} | {comp['Baseline_B_RawCrowd']['unnecessary_reroutes']*100:<22.1f} | {comp['TrustRoute_Proposed']['unnecessary_reroutes']*100:<20.1f}")
    print(f"{'Broken Route Recovery (%)':<32} | {comp['Baseline_A_Static']['broken_route_recovery_rate']*100:<20.1f} | {comp['Baseline_B_RawCrowd']['broken_route_recovery_rate']*100:<22.1f} | {comp['TrustRoute_Proposed']['broken_route_recovery_rate']*100:<20.1f}")
    print(f"{'Avg Travel Time (min)':<32} | {comp['Baseline_A_Static']['avg_travel_time_min']:<20.1f} | {comp['Baseline_B_RawCrowd']['avg_travel_time_min']:<22.1f} | {comp['TrustRoute_Proposed']['avg_travel_time_min']:<20.1f}")
    print(f"{'Avg Transit Fare (INR)':<32} | {comp['Baseline_A_Static']['avg_fare_inr']:<20.1f} | {comp['Baseline_B_RawCrowd']['avg_fare_inr']:<22.1f} | {comp['TrustRoute_Proposed']['avg_fare_inr']:<20.1f}")
    print("-" * 105)
    print(f"\n[*] Summary: {comp_res['executive_summary']}")
    print("=" * 80)


if __name__ == "__main__":
    run_full_evaluation()
