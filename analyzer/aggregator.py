from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analyzer.cicd_parser import normalize_repo_name, parse_cicd
from analyzer.codeql_parser import parse_codeql
from analyzer.counters import (
    common_weakness_ranking,
    count_by_field,
    count_true_field,
    severity_distribution,
    top_codeql_files,
    top_codeql_rules,
)
from analyzer.grype_parser import parse_grype
from analyzer.loaders import load_json_file_with_diagnostics
from analyzer.metrics import risk_score, risk_score_raw, rounded, vulnerability_density
from analyzer.sbom_parser import parse_sbom
from analyzer.validators import (
    ValidationResult,
    validate_cicd,
    validate_codeql,
    validate_grype,
    validate_sbom,
)


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
    cicd_data: dict[str, Any],
) -> dict[str, Any]:
    total_components = int(sbom_data.get("total_components", 0))
    total_vulns = len(vulnerabilities)
    total_codeql = len(codeql_issues)
    total_cicd_findings = int(cicd_data.get("total_findings", 0)) if isinstance(cicd_data, dict) else 0
    by_severity = severity_distribution(vulnerabilities)
    by_type = count_by_field(vulnerabilities, "artifact_type")
    by_rule = count_by_field(codeql_issues, "rule_id")
    by_level = count_by_field(codeql_issues, "level")
    repo_risk_raw = rounded(risk_score_raw(vulnerabilities, total_codeql, total_cicd_findings))
    repo_risk = rounded(risk_score(vulnerabilities, total_codeql, total_cicd_findings))

    return {
        "name": name,
        "sbom": sbom_data,
        "vulnerabilities": {
            "total": total_vulns,
            "severity_distribution": by_severity,
            "by_severity": by_severity,
            "by_artifact_type": by_type,
            "by_type": by_type,
            "with_fix_available": count_true_field(vulnerabilities, "fix_available"),
            "items": vulnerabilities,
        },
        "codeql": {
            "total_issues": total_codeql,
            "by_rule": by_rule,
            "by_level": by_level,
            "top_rules": top_codeql_rules(codeql_issues),
            "top_files": top_codeql_files(codeql_issues),
            "items": codeql_issues,
        },
        "cicd": cicd_data,
        "metrics": {
            "vulnerability_density": vulnerability_density(total_vulns, total_components),
            "risk_score_raw": repo_risk_raw,
            "risk_score": repo_risk,
        },
    }


def build_analysis(
    sbom_files: list[Path],
    vuln_files: list[Path],
    codeql_files: list[Path],
    cicd_files: list[Path],
) -> dict[str, Any]:
    validation_warnings: list[str] = []
    invalid_files: list[str] = []

    def _collect(result: ValidationResult) -> None:
        validation_warnings.extend(result.warnings)
        invalid_files.extend(result.invalid_files)

    sbom_by_repo: dict[str, dict[str, Any]] = {}
    for path in sbom_files:
        load_result = load_json_file_with_diagnostics(path)
        validation_warnings.extend(load_result.warnings)
        invalid_files.extend(load_result.invalid_files)
        if load_result.invalid_files:
            continue
        validation_result = validate_sbom(load_result.data, path)
        _collect(validation_result)
        if not validation_result.valid:
            continue
        sbom_by_repo[_repo_name_from_file(path, "_sbom.json")] = parse_sbom(load_result.data)

    vulns_by_repo: dict[str, list[dict[str, Any]]] = {}
    for path in vuln_files:
        load_result = load_json_file_with_diagnostics(path)
        validation_warnings.extend(load_result.warnings)
        invalid_files.extend(load_result.invalid_files)
        if load_result.invalid_files:
            continue
        validation_result = validate_grype(load_result.data, path)
        _collect(validation_result)
        if not validation_result.valid:
            continue
        vulns_by_repo[_repo_name_from_file(path, "_vuln.json")] = parse_grype(load_result.data)

    codeql_by_repo: dict[str, list[dict[str, Any]]] = {}
    for path in codeql_files:
        load_result = load_json_file_with_diagnostics(path)
        validation_warnings.extend(load_result.warnings)
        invalid_files.extend(load_result.invalid_files)
        if load_result.invalid_files:
            continue
        validation_result = validate_codeql(load_result.data, path)
        _collect(validation_result)
        if not validation_result.valid:
            continue
        codeql_by_repo[_repo_name_from_file(path, "_codeql.sarif")] = parse_codeql(load_result.data)

    cicd_by_repo: dict[str, dict[str, Any]] = {}
    for path in cicd_files:
        load_result = load_json_file_with_diagnostics(path)
        validation_warnings.extend(load_result.warnings)
        invalid_files.extend(load_result.invalid_files)
        if load_result.invalid_files:
            continue
        validation_result = validate_cicd(load_result.data, path)
        _collect(validation_result)
        if not validation_result.valid:
            continue
        parsed = parse_cicd(load_result.data)
        repo_name = normalize_repo_name(load_result.data.get("repo"))
        if repo_name == "unknown":
            repo_name = _repo_name_from_file(path, "_cicd.json")
        cicd_by_repo[repo_name] = parsed

    all_repos = sorted(set(sbom_by_repo) | set(vulns_by_repo) | set(codeql_by_repo) | set(cicd_by_repo))

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
                cicd_data=cicd_by_repo.get(
                    repo,
                    {"workflows_scanned": 0, "total_findings": 0, "items": []},
                ),
            )
        )

    total_components = sum(r["sbom"]["total_components"] for r in repositories)
    all_vulnerabilities = [v for repo in repositories for v in repo["vulnerabilities"]["items"]]
    total_vulnerabilities = len(all_vulnerabilities)
    total_codeql_issues = sum(r["codeql"]["total_issues"] for r in repositories)
    total_cicd_findings = sum(r["cicd"]["total_findings"] for r in repositories)
    cicd_findings_by_repo = sorted(
        (
            {"name": r["name"], "findings": r["cicd"]["total_findings"]}
            for r in repositories
        ),
        key=lambda item: (-item["findings"], item["name"]),
    )

    ranking = sorted(
        (
            {"name": r["name"], "risk_score": r["metrics"]["risk_score"]}
            for r in repositories
        ),
        key=lambda item: (item["risk_score"], item["name"]),
        reverse=True,
    )

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repos_analyzed": len(repositories),
            "data_sources": ["sbom", "grype", "codeql", "cicd"],
            "validation": {
                "warnings": validation_warnings,
                "invalid_files": sorted(set(invalid_files)),
            },
        },
        "repositories": repositories,
        "cross_repo_analysis": {
            "total_components": total_components,
            "total_vulnerabilities": total_vulnerabilities,
            "total_codeql_issues": total_codeql_issues,
            "total_cicd_findings": total_cicd_findings,
            "cicd_findings_by_repo": cicd_findings_by_repo,
            "severity_distribution": severity_distribution(all_vulnerabilities),
            "common_weakness_ranking": common_weakness_ranking(all_vulnerabilities),
            "repo_ranking_by_risk": ranking,
        },
    }
