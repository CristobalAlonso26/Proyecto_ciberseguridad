from __future__ import annotations

from typing import Any


SEVERITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "unknown": 1,
}


def vulnerability_density(total_vulnerabilities: int, total_components: int) -> float:
    return (total_vulnerabilities / max(total_components, 1)) * 100


def risk_score_raw(
    vulnerabilities: list[dict[str, Any]],
    total_codeql_issues: int,
    total_cicd_findings: int,
) -> float:
    _ = total_codeql_issues
    _ = total_cicd_findings

    weighted_sum = 0.0
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity") or "unknown").lower()
        severity_weight = SEVERITY_WEIGHTS.get(severity, 1)
        try:
            vuln_risk = float(vuln.get("risk", 0) or 0)
        except (TypeError, ValueError):
            vuln_risk = 0.0
        weighted_sum += vuln_risk * severity_weight

    vuln_count = len(vulnerabilities)
    if vuln_count == 0:
        return 0.0

    if weighted_sum <= 0:
        return 0.0

    return weighted_sum / max(vuln_count, 1)


def risk_score(vulnerabilities: list[dict[str, Any]], total_codeql_issues: int, total_cicd_findings: int) -> float:
    raw = risk_score_raw(vulnerabilities, total_codeql_issues, total_cicd_findings)
    return max(0.0, min(raw, 10.0))


def rounded(value: float) -> float:
    return round(float(value), 2)
