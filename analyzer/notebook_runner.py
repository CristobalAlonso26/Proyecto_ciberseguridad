from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal


NOTEBOOKS_IN_ORDER = [
    "01_overview.ipynb",
    "02_vulnerability_patterns.ipynb",
    "03_repository_risk_and_conclusions.ipynb",
]

NotebookExecutionStatus = Literal["ok", "missing_jupyter", "notebook_error"]


def execute_notebooks(project_root: Path) -> tuple[NotebookExecutionStatus, str | None]:
    notebooks_dir = project_root / "nbs"
    if not notebooks_dir.exists() or not notebooks_dir.is_dir():
        print("Warning: nbs/ directory not found. Skipping notebook execution.")
        return "ok", None

    for notebook_name in NOTEBOOKS_IN_ORDER:
        notebook_path = notebooks_dir / notebook_name
        if not notebook_path.exists() or not notebook_path.is_file():
            print(f"Warning: notebook not found: {notebook_path}. Skipping.")
            continue

        command = [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            str(notebook_path),
        ]

        try:
            completed = subprocess.run(command, check=False)
        except FileNotFoundError:
            return "missing_jupyter", f"{notebook_path} (missing jupyter command)"

        if completed.returncode != 0:
            return "notebook_error", str(notebook_path)

    return "ok", None
