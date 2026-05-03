from __future__ import annotations

from typing import Any


def normalize_repo_name(repo: str | None) -> str:
    if not repo:
        return "unknown"
    return str(repo).strip().rstrip("/").split("/")[-1] or "unknown"


def parse_cicd(cicd_data: dict[str, Any]) -> dict[str, Any]:
    workflows_scanned = cicd_data.get("workflows_scanned")
    if not isinstance(workflows_scanned, int) or workflows_scanned < 0:
        workflows_scanned = 0

    findings = cicd_data.get("findings")
    if not isinstance(findings, list):
        findings = []

    items: list[dict[str, str]] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue

        workflow = str(finding.get("workflow") or "unknown")
        issues = finding.get("issues")
        if not isinstance(issues, list):
            continue

        for issue in issues:
            if issue in (None, ""):
                continue
            items.append({"workflow": workflow, "issue": str(issue)})

    return {
        "workflows_scanned": workflows_scanned,
        "total_findings": len(items),
        "items": items,
    }
