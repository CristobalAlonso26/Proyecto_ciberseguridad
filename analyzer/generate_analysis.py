from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer.aggregator import build_analysis
from analyzer.loaders import list_files
from analyzer.paths import ANALYSIS_OUTPUT_PATH, CICD_DIR, CODEQL_DIR, SBOMS_DIR, VULNS_DIR
from analyzer.writer import write_json


def main() -> None:
    sbom_files = list_files(SBOMS_DIR, "*_sbom.json")
    vuln_files = list_files(VULNS_DIR, "*_vuln.json")
    codeql_files = list_files(CODEQL_DIR, "*_codeql.sarif")
    cicd_files = list_files(CICD_DIR, "*_cicd.json")

    analysis = build_analysis(
        sbom_files=sbom_files,
        vuln_files=vuln_files,
        codeql_files=codeql_files,
        cicd_files=cicd_files,
    )
    write_json(analysis, ANALYSIS_OUTPUT_PATH)

    print(f"Analysis generated at: {ANALYSIS_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
