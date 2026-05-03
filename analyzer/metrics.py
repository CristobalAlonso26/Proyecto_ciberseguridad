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


def risk_score(vulnerabilities: list[dict[str, Any]], total_codeql_issues: int) -> float:
    weighted_sum = 0.0
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity") or "unknown").lower()
        weighted_sum += SEVERITY_WEIGHTS.get(severity, 1)

    codeql_factor = min(total_codeql_issues / 100, 5)
    return weighted_sum + codeql_factor
