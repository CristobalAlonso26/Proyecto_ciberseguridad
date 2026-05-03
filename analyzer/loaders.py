from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def list_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(directory.glob(pattern))


def load_json_file(file_path: Path) -> dict[str, Any]:
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except (OSError, json.JSONDecodeError):
        return {}
