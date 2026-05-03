from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"
REPORTS_DIR = DATA_DIR / "reports"

SBOMS_DIR = RESULTS_DIR / "sboms"
VULNS_DIR = RESULTS_DIR / "vulns"
CODEQL_DIR = REPORTS_DIR

ANALYSIS_OUTPUT_PATH = RESULTS_DIR / "analysis.json"
