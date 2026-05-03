from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analyzer.codeql_parser import parse_codeql
from analyzer.counters import severity_distribution, top_codeql_files, top_codeql_rules
from analyzer.grype_parser import parse_grype
from analyzer.loaders import load_json_file
from analyzer.metrics import risk_score, vulnerability_density
from analyzer.sbom_parser import parse_sbom


def _repo_name_from_file(file_path: Path, suffix: str) -> str:
    name = file_path.name
    if name.endswith(suffix):
        return name[: -len(suffix)]
    return file_path.stem


def _build_repository_entry(
    name: str,
    sbom_data: dict[str, Any],
    vulnerabilities: list[dict[str, Any]],
    codeql_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    total_components = int(sbom_data.get("total_components", 0))
    total_vulns = len(vulnerabilities)
    total_codeql = len(codeql_issues)

    return {
        "name": name,
        "sbom": sbom_data,
        "vulnerabilities": {
            "total": total_vulns,
            "severity_distribution": severity_distribution(vulnerabilities),
            "items": vulnerabilities,
        },
        "codeql": {
            "total_issues": total_codeql,
            "top_rules": top_codeql_rules(codeql_issues),
            "top_files": top_codeql_files(codeql_issues),
            "items": codeql_issues,
        },
        "metrics": {
            "vulnerability_density": vulnerability_density(total_vulns, total_components),
            "risk_score": risk_score(vulnerabilities, total_codeql),
        },
    }


def build_analysis(
    sbom_files: list[Path],
    vuln_files: list[Path],
    codeql_files: list[Path],
) -> dict[str, Any]:
    sbom_by_repo = {
        _repo_name_from_file(path, "_sbom.json"): parse_sbom(load_json_file(path))
        for path in sbom_files
    }
    vulns_by_repo = {
        _repo_name_from_file(path, "_vuln.json"): parse_grype(load_json_file(path))
        for path in vuln_files
    }
    codeql_by_repo = {
        _repo_name_from_file(path, "_codeql.sarif"): parse_codeql(load_json_file(path))
        for path in codeql_files
    }

    all_repos = sorted(set(sbom_by_repo) | set(vulns_by_repo) | set(codeql_by_repo))

    repositories = []
    for repo in all_repos:
        repositories.append(
            _build_repository_entry(
                name=repo,
                sbom_data=sbom_by_repo.get(
                    repo,
                    {"total_components": 0, "by_type": {}, "by_language": {}},
                ),
                vulnerabilities=vulns_by_repo.get(repo, []),
                codeql_issues=codeql_by_repo.get(repo, []),
            )
        )

    total_components = sum(r["sbom"]["total_components"] for r in repositories)
    all_vulnerabilities = [v for repo in repositories for v in repo["vulnerabilities"]["items"]]
    total_vulnerabilities = len(all_vulnerabilities)
    total_codeql_issues = sum(r["codeql"]["total_issues"] for r in repositories)

    ranking = sorted(
        (
            {"name": r["name"], "risk_score": r["metrics"]["risk_score"]}
            for r in repositories
        ),
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repos_analyzed": len(repositories),
            "data_sources": ["sbom", "grype", "codeql"],
        },
        "repositories": repositories,
        "cross_repo_analysis": {
            "total_components": total_components,
            "total_vulnerabilities": total_vulnerabilities,
            "total_codeql_issues": total_codeql_issues,
            "severity_distribution": severity_distribution(all_vulnerabilities),
            "repo_ranking_by_risk": ranking,
        },
    }
