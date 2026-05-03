from __future__ import annotations

from typing import Any


def parse_codeql(sarif_data: dict[str, Any]) -> list[dict[str, Any]]:
    runs = sarif_data.get("runs")
    if not isinstance(runs, list) or not runs:
        return []

    run0 = runs[0]
    if not isinstance(run0, dict):
        return []

    results = run0.get("results")
    if not isinstance(results, list):
        return []

    issues: list[dict[str, Any]] = []
    for result in results:
        if not isinstance(result, dict):
            continue

        locations = result.get("locations")
        first_location = locations[0] if isinstance(locations, list) and locations else {}
        physical_location = (
            first_location.get("physicalLocation")
            if isinstance(first_location, dict)
            else {}
        )
        if not isinstance(physical_location, dict):
            physical_location = {}

        artifact_location = physical_location.get("artifactLocation")
        if not isinstance(artifact_location, dict):
            artifact_location = {}

        region = physical_location.get("region")
        if not isinstance(region, dict):
            region = {}

        message = result.get("message")
        if not isinstance(message, dict):
            message = {}

        issues.append(
            {
                "rule_id": result.get("ruleId"),
                "message": message.get("text"),
                "file": artifact_location.get("uri"),
                "line": region.get("startLine"),
                "column": region.get("startColumn"),
            }
        )

    return issues
