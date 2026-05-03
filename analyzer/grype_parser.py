from __future__ import annotations

from typing import Any


def _first_list_item(value: Any) -> Any:
    return value[0] if isinstance(value, list) and value else None


def _extract_fix_version(match: dict[str, Any], vulnerability: dict[str, Any]) -> str | None:
    match_detail = _first_list_item(match.get("matchDetails"))
    if isinstance(match_detail, dict):
        detail_fix = match_detail.get("fix")
        if isinstance(detail_fix, dict):
            suggested = detail_fix.get("suggestedVersion")
            if suggested:
                return str(suggested)

    vuln_fix = vulnerability.get("fix")
    if isinstance(vuln_fix, dict):
        versions = vuln_fix.get("versions")
        first_version = _first_list_item(versions)
        if first_version:
            return str(first_version)

    return None


def parse_grype(grype_data: dict[str, Any]) -> list[dict[str, Any]]:
    matches = grype_data.get("matches")
    if not isinstance(matches, list):
        return []

    parsed: list[dict[str, Any]] = []
    for match in matches:
        if not isinstance(match, dict):
            continue

        vulnerability = match.get("vulnerability")
        artifact = match.get("artifact")
        if not isinstance(vulnerability, dict):
            vulnerability = {}
        if not isinstance(artifact, dict):
            artifact = {}

        cvss = _first_list_item(vulnerability.get("cvss"))
        cvss_score = None
        if isinstance(cvss, dict):
            metrics = cvss.get("metrics")
            if isinstance(metrics, dict):
                cvss_score = metrics.get("baseScore")

        epss_item = _first_list_item(vulnerability.get("epss"))
        epss = epss_item.get("epss") if isinstance(epss_item, dict) else None

        cwe_item = _first_list_item(vulnerability.get("cwes"))
        cwe = cwe_item.get("cwe") if isinstance(cwe_item, dict) else None

        locations = artifact.get("locations")
        location = None
        first_location = _first_list_item(locations)
        if isinstance(first_location, dict):
            location = first_location.get("path")

        vuln_fix = vulnerability.get("fix")
        fix_state = vuln_fix.get("state") if isinstance(vuln_fix, dict) else None
        fix_version = _extract_fix_version(match, vulnerability)
        fix_versions = vuln_fix.get("versions") if isinstance(vuln_fix, dict) else None
        has_fix_versions = isinstance(fix_versions, list) and len(fix_versions) > 0
        fix_available = str(fix_state).lower() == "fixed" or has_fix_versions

        parsed.append(
            {
                "id": vulnerability.get("id"),
                "severity": vulnerability.get("severity"),
                "description": vulnerability.get("description"),
                "cvss_score": cvss_score,
                "epss": epss,
                "cwe": cwe,
                "artifact": artifact.get("name"),
                "artifact_version": artifact.get("version"),
                "artifact_type": artifact.get("type"),
                "artifact_language": artifact.get("language"),
                "location": location,
                "fix_state": fix_state,
                "fix_available": fix_available,
                "fix_version": fix_version,
                "risk": vulnerability.get("risk"),
            }
        )

    return parsed
