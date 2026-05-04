from __future__ import annotations

from typing import Any


def _build_rule_levels(run_data: dict[str, Any]) -> dict[str, str]:
    tool = run_data.get("tool")
    if not isinstance(tool, dict):
        return {}

    driver = tool.get("driver")
    if not isinstance(driver, dict):
        return {}

    rules = driver.get("rules")
    if not isinstance(rules, list):
        return {}

    levels: dict[str, str] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("id")
        if not rule_id:
            continue

        default_configuration = rule.get("defaultConfiguration")
        level = None
        if isinstance(default_configuration, dict):
            level = default_configuration.get("level")

        levels[str(rule_id)] = str(level or "unknown")

    return levels


def _extract_issue_level(result: dict[str, Any], rule_levels: dict[str, str]) -> str:
    if result.get("level") not in (None, ""):
        return str(result.get("level"))

    rule_id = result.get("ruleId")
    if rule_id in (None, ""):
        return "unknown"

    return rule_levels.get(str(rule_id), "unknown")


def parse_codeql(sarif_data: dict[str, Any]) -> list[dict[str, Any]]:
    runs = sarif_data.get("runs")
    if not isinstance(runs, list) or not runs:
        return []

    run0 = runs[0]
    if not isinstance(run0, dict):
        return []

    rule_levels = _build_rule_levels(run0)

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
                "level": _extract_issue_level(result, rule_levels),
                "message": message.get("text"),
                "file": artifact_location.get("uri"),
                "line": region.get("startLine"),
                "column": region.get("startColumn"),
            }
        )

    return issues
