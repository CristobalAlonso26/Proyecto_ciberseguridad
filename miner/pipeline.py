import json
import logging
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .clone import clone_repo
from .analyzers.cicd import run_cicd_scan
from .analyzers.codeql import run_codeql
from .analyzers.grype import run_grype
from .analyzers.syft import run_syft
from .github_client import GitHubClient
from .models import Repository

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(
        self,
        token: str,
        org: str,
        clone_root: str = "data/repos",
        results_root: str = "data/results",
        reports_root: str = "data/reports",
        visibility: str = "public",
        limit: int = 50,
        recent_days: int = 30,
        clone_workers: int = 3,
        analysis_workers: int = 2,
        keep_repos: bool = False,
    ) -> None:
        self.client = GitHubClient(token)
        self._token = token
        self.org = org
        self.clone_root = Path(clone_root)
        self.results_root = Path(results_root)
        self.reports_root = Path(reports_root)
        self.visibility = visibility
        self.limit = limit
        self.recent_days = recent_days
        self.clone_workers = clone_workers
        self.analysis_workers = analysis_workers
        self.keep_repos = keep_repos

    def run(self) -> dict:
        logger.info(f"Buscando repos de '{self.org}'...")
        repos = self.client.fetch_active_repos(
            self.org, self.visibility, self.limit, self.recent_days
        )
        logger.info(f"{len(repos)} repos activos encontrados")

        if not repos:
            return {"repos": 0, "cloned": 0, "results": []}

        cloned = self._clone_repos(repos)
        logger.info(f"{len(cloned)} repos clonados")

        results = self._analyze_repos(cloned)

        if not self.keep_repos:
            self._cleanup_repos(cloned)

        return {"repos": len(repos), "cloned": len(cloned), "results": results}

    def _clone_repos(self, repos: list[Repository]) -> list[Repository]:
        cloned = []
        with ThreadPoolExecutor(max_workers=self.clone_workers) as pool:
            futures = {
                pool.submit(clone_repo, r, self.clone_root, self._token): r
                for r in repos
            }
            for f in as_completed(futures):
                repo = futures[f]
                try:
                    path = f.result()
                    repo.clone_path = path
                    cloned.append(repo)
                except Exception as e:
                    logger.error(f"[{repo.full_name}] Error clonando: {e}")
        return cloned

    def _analyze_repos(self, repos: list[Repository]) -> list[dict]:
        results = []
        with ThreadPoolExecutor(max_workers=self.analysis_workers) as pool:
            futures = {
                pool.submit(self._analyze_one, r): r for r in repos
            }
            for f in as_completed(futures):
                repo = futures[f]
                try:
                    result = f.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"[{repo.full_name}] Error analizando: {e}")
                    results.append({"repo": repo.full_name, "error": str(e)})
        return results

    def _analyze_one(self, repo: Repository) -> dict:
        assert repo.clone_path
        t0 = time.time()
        result = {"repo": repo.full_name, "language": repo.language}

        sbom_path = str(self.results_root / "sboms" / f"{repo.name}_sbom.json")
        vuln_path = str(self.results_root / "vulns" / f"{repo.name}_vuln.json")
        codeql_path = str(self.reports_root / f"{repo.name}_codeql.json")
        cicd_path = str(self.reports_root / f"{repo.name}_cicd.json")

        syft_data = run_syft(repo.clone_path, sbom_path)
        result["sbom"] = sbom_path if syft_data else None
        result["sbom_components"] = len(syft_data.get("artifacts", [])) if syft_data else 0

        if syft_data:
            grype_data = run_grype(sbom_path, vuln_path)
            result["vulns"] = vuln_path if grype_data else None
            result["vuln_count"] = len(grype_data.get("matches", [])) if grype_data else 0

        codeql_data = run_codeql(repo.clone_path, codeql_path, repo.language)
        result["codeql"] = codeql_path if codeql_data else None
        result["codeql_findings"] = codeql_data.get("total_issues", 0) if codeql_data else 0

        cicd_data = run_cicd_scan(repo.clone_path, repo.full_name)
        result["cicd"] = cicd_path
        result["cicd_findings"] = sum(len(f["issues"]) for f in cicd_data.get("findings", []))
        Path(cicd_path).parent.mkdir(parents=True, exist_ok=True)
        Path(cicd_path).write_text(json.dumps(cicd_data, indent=2, default=str))

        result["duration_s"] = round(time.time() - t0, 1)
        logger.info(
            f"[{repo.full_name}] completado en {result['duration_s']}s: "
            f"{result['sbom_components']} deps, {result.get('vuln_count', 0)} vulns, "
            f"{result['codeql_findings']} codeql, {result['cicd_findings']} cicd"
        )
        return result

    def _cleanup_repos(self, repos: list[Repository]) -> None:
        for repo in repos:
            if repo.clone_path and Path(repo.clone_path).exists():
                try:
                    shutil.rmtree(repo.clone_path)
                    logger.debug(f"[{repo.full_name}] Repo clonado eliminado")
                except Exception as e:
                    logger.warning(f"[{repo.full_name}] Error eliminando repo: {e}")
