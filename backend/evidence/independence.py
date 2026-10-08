"""
Independence & Copy-Ring Detection Module.
Distinguishes between honest independent duplicates and coordinated/copied echoes.
Maintains evidence provenance to prevent copy-rings from falsely corroborating rumours.
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple, Set
from backend.evidence.schemas import GroundedEvidence, EvidenceProvenance, IndependenceType, SourceType


def normalize_text_for_comparison(text: str) -> Set[str]:
    """Tokenizes and normalizes text into a set of lowercased alphanumeric words."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    tokens = [w for w in cleaned.split() if len(w) > 2]
    return set(tokens)


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Computes token Jaccard similarity between two text strings."""
    tokens1 = normalize_text_for_comparison(text1)
    tokens2 = normalize_text_for_comparison(text2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


class IndependenceEngine:
    """Evaluates source independence, duplication, and copy-ring echo behavior."""

    def __init__(self, burst_window_minutes: int = 10, similarity_threshold: float = 0.80):
        self.burst_window_minutes = burst_window_minutes
        self.similarity_threshold = similarity_threshold

    def evaluate_independence(
        self,
        new_item: GroundedEvidence,
        existing_items: List[GroundedEvidence]
    ) -> EvidenceProvenance:
        """
        Determines whether new_item is an independent report, an honest duplicate,
        a copy-ring derivation, or unknown.
        """
        evidence_id = new_item.extracted.source_id
        source_type = new_item.extracted.source_type
        author_id = new_item.extracted.source_id  # Fallback to source_id if author not set

        if not existing_items:
            # First item in cluster is always independent
            return EvidenceProvenance(
                evidence_id=evidence_id,
                source_id=new_item.extracted.source_id,
                source_type=source_type,
                author_id=author_id,
                independence=IndependenceType.INDEPENDENT,
                parent_evidence_id=None,
                similarity_score=0.0,
                burst_detected=False
            )

        # Check against existing items in cluster
        best_similarity = 0.0
        parent_id = None
        is_exact_author_duplicate = False
        is_copy_derived = False

        for prev in existing_items:
            prev_src_id = prev.extracted.source_id
            
            # 1. Exact same source / author duplication
            if prev_src_id == new_item.extracted.source_id:
                is_exact_author_duplicate = True
                parent_id = prev_src_id
                break

            # 2. Text similarity & burst window check
            sim = calculate_jaccard_similarity(new_item.extracted.raw_text, prev.extracted.raw_text)
            if sim > best_similarity:
                best_similarity = sim
                parent_id = prev_src_id

            # Burst window timing
            time_diff_mins = abs((new_item.extracted.timestamp - prev.extracted.timestamp).total_seconds()) / 60.0

            # Copy-Ring heuristic: High similarity within short burst window
            if sim >= self.similarity_threshold and time_diff_mins <= self.burst_window_minutes:
                # If exact copy or word-for-word copy from different source
                is_copy_derived = True
                break

        # Decision logic
        if is_exact_author_duplicate:
            indep_type = IndependenceType.DUPLICATE
        elif is_copy_derived:
            indep_type = IndependenceType.COPY_DERIVED
        elif best_similarity >= 0.85:
            # High similarity but outside burst window: duplicate
            indep_type = IndependenceType.DUPLICATE
        else:
            # Distinct wording, separate report -> honest independent observation
            indep_type = IndependenceType.INDEPENDENT

        return EvidenceProvenance(
            evidence_id=evidence_id,
            source_id=new_item.extracted.source_id,
            source_type=source_type,
            author_id=author_id,
            independence=indep_type,
            parent_evidence_id=parent_id if indep_type != IndependenceType.INDEPENDENT else None,
            similarity_score=best_similarity,
            burst_detected=is_copy_derived
        )
