"""
Strict Validation Module for Evidence & Trust Engine.
Validates schemas, data types, timestamps, severity, and disruption types.
"""

from typing import Dict, Any, Tuple
from pydantic import ValidationError
from backend.evidence.schemas import RawEvidenceInput, ExtractedEvidence, Severity, DisruptionType, DisruptionStatus


class EvidenceValidator:
    """Validates raw and extracted evidence against strict Pydantic models."""

    @staticmethod
    def validate_raw_input(data: Dict[str, Any]) -> Tuple[bool, RawEvidenceInput | None, str | None]:
        """
        Validate incoming raw evidence dictionary.
        Returns (is_valid, validated_model, error_message).
        """
        try:
            validated = RawEvidenceInput.model_validate(data)
            return True, validated, None
        except ValidationError as e:
            return False, None, f"Raw evidence validation error: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected validation error: {str(e)}"

    @staticmethod
    def validate_extracted_evidence(data: Dict[str, Any]) -> Tuple[bool, ExtractedEvidence | None, str | None]:
        """
        Validate LLM or parser extracted fields.
        Applies fallback default severity (MEDIUM) if missing or UNKNOWN,
        while flagging severity_inferred = True.
        """
        try:
            # Ensure severity default rule
            sev_val = data.get("severity")
            severity_inferred = False
            if not sev_val or str(sev_val).upper() in ("UNKNOWN", "NONE", "NULL"):
                data["severity"] = Severity.MEDIUM
                severity_inferred = True
            
            # Standardize disruption type
            dtype = data.get("disruption_type")
            if not dtype:
                data["disruption_type"] = DisruptionType.UNKNOWN
            elif isinstance(dtype, str):
                try:
                    data["disruption_type"] = DisruptionType(dtype.upper())
                except ValueError:
                    data["disruption_type"] = DisruptionType.UNKNOWN

            # Standardize status
            status_val = data.get("status")
            if not status_val:
                data["status"] = DisruptionStatus.ACTIVE
            elif isinstance(status_val, str):
                try:
                    data["status"] = DisruptionStatus(status_val.upper())
                except ValueError:
                    data["status"] = DisruptionStatus.ACTIVE

            validated = ExtractedEvidence.model_validate(data)
            validated.severity_inferred = severity_inferred
            return True, validated, None
        except ValidationError as e:
            return False, None, f"Extracted evidence validation error: {str(e)}"
        except Exception as e:
            return False, None, f"Extraction validation error: {str(e)}"
