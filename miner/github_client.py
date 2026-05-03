import logging
import time
from datetime import datetime
from typing import Any

import requests

from .models import Repository

logger = logging.getLogger(__name__)


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def get_org(self, org: str) -> dict[str, Any]:
        r = self._session.get(f"{self.BASE_URL}/orgs/{org}")
        r.raise_for_status()
        return r.json()

    def list_org_repos(
        self,
        org: str,
        visibility: str = "public",
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        all_repos: list[dict[str, Any]] = []
        url = f"{self.BASE_URL}/orgs/{org}/repos"
        params = {"per_page": per_page, "type": visibility, "sort": "full_name"}

        while url:
            r = self._session.get(url, params=params)
            r.raise_for_status()
            repos = r.json()

            if not isinstance(repos, list):
                error = repos.get("message", "Unknown error")
                raise RuntimeError(f"Error de GitHub API: {error}")

            all_repos.extend(repos)
            url = self._next_link(r.headers.get("Link", ""))
            params = {}

        return all_repos

    @staticmethod
    def _next_link(link_header: str) -> str | None:
        if not link_header:
            return None
        for part in link_header.split(","):
            url_part, *rel_parts = part.strip().split(";")
            if any('rel="next"' in r for r in rel_parts):
                return url_part.strip().strip("<>")
        return None

    def fetch_active_repos(
        self,
        org: str,
        visibility: str = "public",
        limit: int = 50,
        recent_days: int = 30,
    ) -> list[Repository]:
        cutoff = time.time() - (recent_days * 86400)
        all_repos = self.list_org_repos(org, visibility)

        active = []
        for data in all_repos:
            if data.get("archived"):
                continue
            pushed = data.get("pushed_at")
            if pushed:
                ts = datetime.fromisoformat(pushed.replace("Z", "+00:00")).timestamp()
                if ts < cutoff:
                    continue
            active.append(Repository.from_api(data))

        active.sort(key=lambda r: r.pushed_at or datetime.min, reverse=True)
        return active[:limit]
