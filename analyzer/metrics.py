from __future__ import annotations

from typing import Any

GRYPE_SEVERITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "unknown": 1,
}

CODEQL_LEVEL_WEIGHTS = {
    "error": 4,
    "warning": 2,
    "note": 1,
}

SMOOTHING_FACTOR = 5


def vulnerability_density(total_vulnerabilities: int, total_components: int) -> float:
    return (total_vulnerabilities / max(total_components, 1)) * 100


def _grype_weight(vulnerabilities: list[dict[str, Any]]) -> float:
    total = 0.0
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity") or "").strip().lower()
        total += GRYPE_SEVERITY_WEIGHTS.get(severity, 1)
    return total


def _codeql_weight(codeql_issues: list[dict[str, Any]]) -> float:
    total = 0.0
    for issue in codeql_issues:
        level = str(issue.get("level") or "").strip().lower()
        total += CODEQL_LEVEL_WEIGHTS.get(level, 1)
    return total


def risk_score_raw(
    vulnerabilities: list[dict[str, Any]],
    codeql_issues: list[dict[str, Any]],
) -> float:
    total_weight = _grype_weight(vulnerabilities) + _codeql_weight(codeql_issues)
    total_items = len(vulnerabilities) + len(codeql_issues)
    return total_weight / (total_items + SMOOTHING_FACTOR)


def risk_score(
    vulnerabilities: list[dict[str, Any]],
    codeql_issues: list[dict[str, Any]],
) -> float:
    return rounded(risk_score_raw(vulnerabilities, codeql_issues))


def rounded(value: float) -> float:
    return round(float(value), 2)
