from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def list_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(directory.glob(pattern))


@dataclass
class LoadResult:
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    invalid_files: list[str] = field(default_factory=list)


def load_json_file(file_path: Path) -> dict[str, Any]:
    return load_json_file_with_diagnostics(file_path).data


def load_json_file_with_diagnostics(file_path: Path) -> LoadResult:
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return LoadResult(data=data)
        warning = f"Invalid JSON root in {file_path}: expected object"
        return LoadResult(data={}, warnings=[warning], invalid_files=[str(file_path)])
    except OSError as exc:
        warning = f"Error reading JSON file {file_path}: {exc}"
        return LoadResult(data={}, warnings=[warning], invalid_files=[str(file_path)])
    except json.JSONDecodeError as exc:
        warning = f"Invalid JSON in {file_path}: {exc.msg}"
        return LoadResult(data={}, warnings=[warning], invalid_files=[str(file_path)])
