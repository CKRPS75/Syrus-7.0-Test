"""
TrustRoute Reproducibility & Audit Logger (Task 13).
Captures system fingerprint, parameter hashes, dataset checksums, and execution settings
before held-out benchmark evaluation runs.
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any


class ReproducibilityAuditor:
    """Computes and validates reproducibility signatures."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def compute_sha256(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return "NOT_FOUND"
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()

    def get_git_commit(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=3
            )
            return res.stdout.strip() if res.returncode == 0 else "GIT_NOT_FOUND"
        except Exception:
            return "UNTRACKED"

    def generate_audit_log(self, seed: int = 42) -> Dict[str, Any]:
        params_path = os.path.join(self.base_dir, "config", "parameters.json")
        reference_path = os.path.join(self.base_dir, "data", "mumbai_reference.json")
        benchmark_path = os.path.join(self.base_dir, "data", "benchmark_30_reports.json")

        audit_record = {
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": self.get_git_commit(),
            "random_seed": seed,
            "python_version": sys.version,
            "platform": sys.platform,
            "parameter_hash_sha256": self.compute_sha256(params_path),
            "reference_data_sha256": self.compute_sha256(reference_path),
            "benchmark_dataset_sha256": self.compute_sha256(benchmark_path),
            "otp_engine_version": "2.10.x-compatible",
            "evaluator_version": "2.0.0"
        }
        return audit_record

    def save_audit_log(self, output_path: str = None) -> str:
        if output_path is None:
            output_path = os.path.join(self.base_dir, "evaluation", "reproducibility_audit.json")
        
        record = self.generate_audit_log()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        return output_path


if __name__ == "__main__":
    auditor = ReproducibilityAuditor()
    path = auditor.save_audit_log()
    print(f"Reproducibility audit record saved to: {path}")
