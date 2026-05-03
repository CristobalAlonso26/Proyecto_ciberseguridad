import json
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: list[dict[str, Any]]) -> None:
        self._path.write_text(json.dumps(data, indent=2, default=str))

    def load(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        return json.loads(self._path.read_text())
