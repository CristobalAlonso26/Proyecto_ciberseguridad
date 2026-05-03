from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _without_generated_at(analysis: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = dict(analysis)
    metadata = normalized.get("metadata")

    if isinstance(metadata, dict):
        metadata_copy = dict(metadata)
        metadata_copy.pop("generated_at", None)
        normalized["metadata"] = metadata_copy

    return normalized


def compute_analysis_hash(analysis: dict[str, Any]) -> str:
    normalized = _without_generated_at(analysis)
    serialized = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def load_previous_hash(state_path: Path) -> str | None:
    try:
        with state_path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(state, dict):
        return None

    hash_value = state.get("analysis_hash")
    return hash_value if isinstance(hash_value, str) and hash_value else None


def save_analysis_hash(state_path: Path, analysis_hash: str) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"analysis_hash": analysis_hash}
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
