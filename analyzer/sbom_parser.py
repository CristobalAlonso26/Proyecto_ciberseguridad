from __future__ import annotations

from collections import Counter
from typing import Any


def parse_sbom(sbom_data: dict[str, Any]) -> dict[str, Any]:
    artifacts = sbom_data.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = []

    by_type: Counter[str] = Counter()
    by_language: Counter[str] = Counter()

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_type = str(artifact.get("type") or "unknown")
        artifact_language = str(artifact.get("language") or "unknown")
        by_type[artifact_type] += 1
        by_language[artifact_language] += 1

    return {
        "total_components": len(artifacts),
        "by_type": dict(by_type),
        "by_language": dict(by_language),
    }
