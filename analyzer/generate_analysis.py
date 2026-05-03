from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer.analysis_state import compute_analysis_hash, load_previous_hash, save_analysis_hash
from analyzer.aggregator import build_analysis
from analyzer.loaders import list_files
from analyzer.notebook_runner import execute_notebooks
from analyzer.paths import ANALYSIS_OUTPUT_PATH, ANALYSIS_STATE_PATH, CICD_DIR, CODEQL_DIR, PROJECT_ROOT, SBOMS_DIR, VULNS_DIR
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

    current_hash = compute_analysis_hash(analysis)
    previous_hash = load_previous_hash(ANALYSIS_STATE_PATH)

    if previous_hash == current_hash:
        print("Analysis unchanged. Skipping notebook execution.")
        return

    notebook_status, notebook_detail = execute_notebooks(PROJECT_ROOT)
    if notebook_status == "missing_jupyter":
        print(
            "Warning: notebook execution skipped because jupyter is not installed or not available in PATH."
        )
        return

    if notebook_status == "notebook_error":
        print(f"Notebook failed: {notebook_detail}")
        raise RuntimeError(f"Notebook execution failed: {notebook_detail}")

    save_analysis_hash(ANALYSIS_STATE_PATH, current_hash)


if __name__ == "__main__":
    main()
