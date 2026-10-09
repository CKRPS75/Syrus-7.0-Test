from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.db.models import ReportModel, EventModel, EvidenceModel


class BaseEvidenceProcessor(ABC):
    @abstractmethod
    def process_report(
        self,
        report_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Parses raw report data and returns structured dicts for:
        (event_dict, evidence_dict, report_dict)
        """
        pass
