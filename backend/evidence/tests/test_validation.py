"""
Unit tests for Pydantic Validation and Schema Enforcement.
"""

from datetime import datetime, timezone
from backend.evidence.validator import EvidenceValidator


def test_valid_raw_input_validation():
    data = {
        "source_id": "SRC_01",
        "source_type": "crowd",
        "text": "Delay at Bandra station.",
        "timestamp": "2026-10-08T18:00:00Z"
    }
    is_valid, validated, err = EvidenceValidator.validate_raw_input(data)
    assert is_valid is True
    assert validated is not None
    assert validated.source_id == "SRC_01"
    assert err is None


def test_empty_text_rejection():
    data = {
        "source_id": "SRC_02",
        "source_type": "crowd",
        "text": "   ",
        "timestamp": "2026-10-08T18:00:00Z"
    }
    is_valid, validated, err = EvidenceValidator.validate_raw_input(data)
    assert is_valid is False
    assert validated is None
    assert "Evidence text must not be empty" in str(err)


def test_missing_timestamp_rejection():
    data = {
        "source_id": "SRC_03",
        "source_type": "crowd",
        "text": "Delay at Bandra"
    }
    is_valid, validated, err = EvidenceValidator.validate_raw_input(data)
    assert is_valid is False
    assert validated is None
    assert "Field required" in str(err)


def test_invalid_source_type_rejection():
    data = {
        "source_id": "SRC_04",
        "source_type": "telepathic_rumour",
        "text": "Something happened",
        "timestamp": "2026-10-08T18:00:00Z"
    }
    is_valid, validated, err = EvidenceValidator.validate_raw_input(data)
    assert is_valid is False
    assert validated is None
