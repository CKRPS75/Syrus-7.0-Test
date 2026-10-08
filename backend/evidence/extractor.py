"""
LLM Extraction & Anti-Injection Parsing Module.
Dynamically extracts structured transit disruption attributes from unstructured text.
Supports Google Gemini API (GEMINI_API_KEY) and OpenAI API (OPENAI_API_KEY)
with automatic fallback to reference-driven dynamic NLP parser.
Hardened against prompt injections and malicious instruction overrides.
"""

import os
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

from backend.evidence.schemas import (
    RawEvidenceInput,
    ExtractedEvidence,
    Severity,
    DisruptionType,
    DisruptionStatus
)
from backend.evidence.validator import EvidenceValidator


DEFAULT_DISRUPTION_PATTERNS = [
    (r"\b(delay|delayed|delaying|late|waiting|stuck|slow|snag|crawl|held up)\b", DisruptionType.DELAY),
    (r"\b(cancel|cancelled|cancelling|not running|curtailed)\b", DisruptionType.CANCELLATION),
    (r"\b(suspend|suspended|suspension|stopped|halted|stalled|paralysed|paralyzed)\b", DisruptionType.SUSPENSION),
    (r"\b(close|closed|closure|shut|shutting)\b", DisruptionType.CLOSURE),
    (r"\b(derail|derailment|accident|breakdown|fire|smoke|snapped)\b", DisruptionType.ACCIDENT),
    (r"\b(maintenance|megablock|mega block|jumbo block|engineering work|repair)\b", DisruptionType.MAINTENANCE),
    (r"\b(crowd|crowded|congestion|rush|stampede-like|packed)\b", DisruptionType.CONGESTION),
    (r"\b(restored|normal|cleared|operating normally|on time|all clear|running smoothly|resumed)\b", DisruptionType.NORMAL_OPERATION),
]

DEFAULT_SEVERITY_PATTERNS = [
    (r"\b(severe|massive|major|closed|halted|derail|shut|deadlock|> 30|30 min|45 min|1 hour|indefinite)\b", Severity.HIGH),
    (r"\b(minor|slight|small|5 min|< 10 min|brief)\b", Severity.LOW),
    (r"\b(delayed|waiting|moderate|crowded|20 min|15 min|noticeable)\b", Severity.MEDIUM),
]


class EvidenceExtractor:
    """Extracts structured transit facts using Gemini, OpenAI, or dynamic reference parser."""

    def __init__(
        self,
        prompt_path: Optional[str] = None,
        reference_path: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.prompt_path = prompt_path or os.path.join(base_dir, "prompts", "evidence_extraction.txt")
        self.reference_path = reference_path or os.path.join(base_dir, "data", "mumbai_reference.json")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        self.system_prompt = self._load_prompt()
        self.dynamic_locations: List[Tuple[str, str]] = []  # (alias, standard_name)
        self.dynamic_routes: List[Tuple[str, str]] = []     # (regex_or_alias, route_id)
        self._load_dynamic_reference_entities()

    def _load_prompt(self) -> str:
        if os.path.exists(self.prompt_path):
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Extract transit disruption facts strictly as JSON."

    def _load_dynamic_reference_entities(self) -> None:
        """Dynamically loads and indexes any City Pack reference data without hardcoding city names."""
        if not os.path.exists(self.reference_path):
            return

        with open(self.reference_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build stop/location vocabulary sorted by alias length descending
        stops_list = []
        for stop in data.get("stops", []):
            s_name = stop.get("stop_name", "")
            s_id = stop.get("stop_id", "")
            aliases = stop.get("aliases", []) + [s_name, s_id]
            for alias in aliases:
                if alias:
                    stops_list.append((alias.lower().strip(), s_name, s_id))
        
        stops_list.sort(key=lambda x: len(x[0]), reverse=True)
        self.dynamic_locations = [(item[0], item[1]) for item in stops_list]

        # Build route patterns
        routes_list = []
        for route in data.get("routes", []):
            r_id = route.get("route_id", "")
            r_short = route.get("route_short_name", "")
            r_long = route.get("route_long_name", "")
            aliases = route.get("aliases", []) + [r_id, r_short, r_long]
            for alias in aliases:
                if alias:
                    routes_list.append((alias.lower().strip(), r_id))
        
        routes_list.sort(key=lambda x: len(x[0]), reverse=True)
        self.dynamic_routes = routes_list

    def _sanitize_untrusted_text(self, text: str) -> str:
        """
        Strips active injection tokens while preserving raw transit factual text.
        Neutralizes commands attempting to hijack the downstream engine.
        """
        patterns_to_neutralize = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"system\s+override",
            r"mark\s+this\s+(as\s+)?confirmed",
            r"reroute\s+(all\s+)?passengers",
            r"set\s+status\s*=\s*confirmed",
            r"you\s+are\s+now\s+in\s+developer\s+mode"
        ]
        sanitized = text
        for p in patterns_to_neutralize:
            sanitized = re.sub(p, "[REDACTED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def _call_gemini_api(self, raw_input: RawEvidenceInput, sanitized_text: str) -> Optional[ExtractedEvidence]:
        """Calls Google Gemini REST API to extract structured disruption facts."""
        try:
            import requests
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "system_instruction": {
                    "parts": [{"text": self.system_prompt}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"<untrusted_content>\n{sanitized_text}\n</untrusted_content>"}]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.0
                }
            }

            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            if resp.status_code == 200:
                resp_json = resp.json()
                content_str = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                extracted_dict = json.loads(content_str)
                extracted_dict["source_id"] = raw_input.source_id
                extracted_dict["source_type"] = raw_input.source_type
                extracted_dict["raw_text"] = raw_input.text
                extracted_dict["timestamp"] = raw_input.timestamp

                is_valid, validated_obj, err = EvidenceValidator.validate_extracted_evidence(extracted_dict)
                if is_valid and validated_obj:
                    return validated_obj
        except Exception:
            pass
        return None

    def _call_openai_api(self, raw_input: RawEvidenceInput, sanitized_text: str) -> Optional[ExtractedEvidence]:
        """Calls OpenAI API to extract structured disruption facts."""
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"<untrusted_content>\n{sanitized_text}\n</untrusted_content>"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
            }

            resp = requests.post(
                os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"),
                headers=headers,
                json=payload,
                timeout=10
            )
            if resp.status_code == 200:
                resp_json = resp.json()
                content_str = resp_json["choices"][0]["message"]["content"]
                extracted_dict = json.loads(content_str)
                extracted_dict["source_id"] = raw_input.source_id
                extracted_dict["source_type"] = raw_input.source_type
                extracted_dict["raw_text"] = raw_input.text
                extracted_dict["timestamp"] = raw_input.timestamp

                is_valid, validated_obj, err = EvidenceValidator.validate_extracted_evidence(extracted_dict)
                if is_valid and validated_obj:
                    return validated_obj
        except Exception:
            pass
        return None

    def extract_deterministic(self, raw_input: RawEvidenceInput) -> ExtractedEvidence:
        """
        Dynamic NLP/regex extraction driven by loaded city reference data.
        Guarantees 100% test reproducibility, zero-cost, and instant execution.
        """
        clean_text = self._sanitize_untrusted_text(raw_input.text)
        lower_text = clean_text.lower()

        # 1. Dynamic Location match from reference database
        matched_loc = None
        for alias, standard_name in self.dynamic_locations:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, lower_text):
                matched_loc = standard_name
                break

        # 2. Dynamic Route match from reference database
        matched_route = None
        for alias, route_id in self.dynamic_routes:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, lower_text):
                matched_route = route_id
                break

        # 3. Disruption type match
        matched_dtype = DisruptionType.UNKNOWN
        for pattern, dtype in DEFAULT_DISRUPTION_PATTERNS:
            if re.search(pattern, lower_text, re.IGNORECASE):
                matched_dtype = dtype
                break

        # 4. Severity match
        matched_sev = Severity.UNKNOWN
        for pattern, sev in DEFAULT_SEVERITY_PATTERNS:
            if re.search(pattern, lower_text, re.IGNORECASE):
                matched_sev = sev
                break

        # If severity is unknown, default to MEDIUM and mark inferred
        severity_inferred = False
        if matched_sev == Severity.UNKNOWN:
            matched_sev = Severity.MEDIUM
            severity_inferred = True

        # 5. Status match
        matched_status = DisruptionStatus.ACTIVE
        if matched_dtype == DisruptionType.NORMAL_OPERATION or "restor" in lower_text or "cleared" in lower_text or "resumed" in lower_text:
            matched_status = DisruptionStatus.RESOLVED

        return ExtractedEvidence(
            source_id=raw_input.source_id,
            source_type=raw_input.source_type,
            raw_text=raw_input.text,
            location=matched_loc,
            route_id=matched_route,
            stop_id=matched_loc.upper() if matched_loc else None,
            trip_id=None,
            disruption_type=matched_dtype,
            severity=matched_sev,
            severity_inferred=severity_inferred,
            timestamp=raw_input.timestamp,
            status=matched_status,
            description=clean_text[:200]
        )

    def extract(self, raw_input: RawEvidenceInput) -> ExtractedEvidence:
        """
        Extracts structured transit facts using Gemini (if GEMINI_API_KEY is present),
        OpenAI (if OPENAI_API_KEY is present), or dynamic reference-driven parser.
        """
        sanitized_text = self._sanitize_untrusted_text(raw_input.text)

        # 1. Try Google Gemini API if key is present
        if self.gemini_api_key:
            extracted = self._call_gemini_api(raw_input, sanitized_text)
            if extracted:
                return extracted

        # 2. Try OpenAI API if key is present
        if self.openai_api_key:
            extracted = self._call_openai_api(raw_input, sanitized_text)
            if extracted:
                return extracted

        # 3. Dynamic Reference-driven NLP Fallback
        return self.extract_deterministic(raw_input)
