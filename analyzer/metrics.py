from __future__ import annotations

from typing import Any


SEVERITY_POINTS = {
    "critical": 10,
    "high": 6,
    "medium": 3,
    "low": 1,
}


def vulnerability_density(total_vulnerabilities: int, total_components: int) -> float:
    return (total_vulnerabilities / max(total_components, 1)) * 100


def risk_score_raw(
    vulnerabilities: list[dict[str, Any]],
    total_codeql_issues: int,
    total_cicd_findings: int,
) -> float:
    severity_points = 0.0
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity") or "").strip().lower()
        severity_points += SEVERITY_POINTS.get(severity, 0)

    codeql_points = max(float(total_codeql_issues or 0), 0.0) * 0.5
    cicd_points = max(float(total_cicd_findings or 0), 0.0) * 2

    return rounded(severity_points + codeql_points + cicd_points)


def risk_score(vulnerabilities: list[dict[str, Any]], total_codeql_issues: int, total_cicd_findings: int) -> float:
    raw = risk_score_raw(vulnerabilities, total_codeql_issues, total_cicd_findings)
    return rounded(min(raw / 10, 10))


def rounded(value: float) -> float:
    return round(float(value), 2)
