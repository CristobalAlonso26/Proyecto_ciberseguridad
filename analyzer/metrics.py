from __future__ import annotations

import math
from typing import Any

SEVERITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

GRYPE_WEIGHT = 0.6
CODEQL_WEIGHT = 0.2
CICD_WEIGHT = 0.2


def vulnerability_density(total_vulnerabilities: int, total_components: int) -> float:
    return (total_vulnerabilities / max(total_components, 1)) * 100


def risk_score_raw(
    vulnerabilities: list[dict[str, Any]],
    total_codeql_issues: int,
    total_cicd_findings: int,
) -> float:
    weighted_sum = 0.0
    valid_count = 0
    for vuln in vulnerabilities:
        risk = vuln.get("risk")
        if not isinstance(risk, (int, float)) or risk < 0:
            continue
        severity = str(vuln.get("severity") or "").strip().lower()
        weight = SEVERITY_WEIGHTS.get(severity, 1)
        weighted_sum += risk * weight
        valid_count += 1

    grype_component = weighted_sum / max(valid_count, 1)

    codeql_component = min(math.log1p(max(float(total_codeql_issues or 0), 0.0)) * 2, 10)
    cicd_component = min(math.log1p(max(float(total_cicd_findings or 0), 0.0)) * 3, 10)

    return rounded(
        grype_component * GRYPE_WEIGHT
        + codeql_component * CODEQL_WEIGHT
        + cicd_component * CICD_WEIGHT
    )


def risk_score(vulnerabilities: list[dict[str, Any]], total_codeql_issues: int, total_cicd_findings: int) -> float:
    raw = risk_score_raw(vulnerabilities, total_codeql_issues, total_cicd_findings)
    return rounded(min(raw, 10))


def rounded(value: float) -> float:
    return round(float(value), 2)
