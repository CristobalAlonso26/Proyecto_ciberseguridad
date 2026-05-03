from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass
class Repository:
    name: str
    full_name: str
    clone_url: str
    language: str | None = None
    pushed_at: datetime | None = None
    clone_path: str | None = None

    @property
    def org_name(self) -> str:
        return self.full_name.split("/")[0]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Repository:
        return cls(
            name=data["name"],
            full_name=data["full_name"],
            clone_url=data["clone_url"],
            language=data.get("language"),
            pushed_at=_parse_dt(data.get("pushed_at")),
        )
