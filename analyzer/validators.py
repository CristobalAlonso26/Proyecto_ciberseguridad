from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    valid: bool
    warnings: list[str] = field(default_factory=list)
    invalid_files: list[str] = field(default_factory=list)


def _invalid(source: str, path: Path, reason: str) -> ValidationResult:
    path_str = str(path)
    warning = f"Invalid {source} file {path_str}: {reason}"
    return ValidationResult(valid=False, warnings=[warning], invalid_files=[path_str])


def _valid() -> ValidationResult:
    return ValidationResult(valid=True)


def validate_sbom(data: dict[str, Any], path: Path) -> ValidationResult:
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        return _invalid("SBOM", path, "missing key artifacts or not a list")
    return _valid()


def validate_grype(data: dict[str, Any], path: Path) -> ValidationResult:
    matches = data.get("matches")
    if not isinstance(matches, list):
        return _invalid("Grype", path, "missing key matches or not a list")
    return _valid()


def validate_codeql(data: dict[str, Any], path: Path) -> ValidationResult:
    runs = data.get("runs")
    if not isinstance(runs, list):
        return _invalid("CodeQL SARIF", path, "missing key runs or not a list")
    return _valid()


def validate_codeql_normalized(data: dict[str, Any], path: Path) -> ValidationResult:
    if "findings" in data:
        if isinstance(data.get("findings"), list):
            return _valid()
        return _invalid("CodeQL normalized", path, "key findings is not a list")

    if "results" in data:
        if isinstance(data.get("results"), list):
            return _valid()
        return _invalid("CodeQL normalized", path, "key results is not a list")

    # Estructura alternativa aceptada en algunos exports
    if isinstance(data.get("runs"), list):
        return _valid()

    return _invalid(
        "CodeQL normalized",
        path,
        "unrecognized structure (expected findings/results/runs)",
    )


def validate_cicd(data: dict[str, Any], path: Path) -> ValidationResult:
    required_keys = ["repo", "workflows_scanned", "findings"]
    missing = [key for key in required_keys if key not in data]
    if missing:
        return _invalid("CI/CD", path, f"missing keys: {', '.join(missing)}")

    if not isinstance(data.get("findings"), list):
        return _invalid("CI/CD", path, "key findings is not a list")

    return _valid()
