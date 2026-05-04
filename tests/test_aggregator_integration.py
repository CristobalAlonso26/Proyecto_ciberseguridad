import json

from analyzer.aggregator import build_analysis


def test_build_analysis_with_synthetic_inputs_and_invalid_file(tmp_path) -> None:
    sbom_file = tmp_path / "repo1_sbom.json"
    vuln_file = tmp_path / "repo1_vuln.json"
    codeql_file = tmp_path / "repo1_codeql.sarif"
    cicd_file = tmp_path / "repo1_cicd.json"
    invalid_sbom_file = tmp_path / "repo2_sbom.json"

    sbom_file.write_text(
        json.dumps({"artifacts": [{"type": "npm", "language": "JavaScript"}]}),
        encoding="utf-8",
    )
    vuln_file.write_text(
        json.dumps(
            {
                "matches": [
                    {
                        "vulnerability": {"id": "CVE-1", "severity": "Low", "risk": 1},
                        "artifact": {"type": "npm", "name": "pkg"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    codeql_file.write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "results": [
                            {
                                "ruleId": "js/xss",
                                "level": "warning",
                                "message": {"text": "xss"},
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    cicd_file.write_text(
        json.dumps(
            {
                "repo": "org/repo1",
                "workflows_scanned": 1,
                "findings": [{"workflow": "ci.yml", "issues": ["unpinned action"]}],
            }
        ),
        encoding="utf-8",
    )
    invalid_sbom_file.write_text(json.dumps({"not_artifacts": []}), encoding="utf-8")

    analysis = build_analysis(
        sbom_files=[sbom_file, invalid_sbom_file],
        vuln_files=[vuln_file],
        codeql_files=[codeql_file],
        cicd_files=[cicd_file],
    )

    assert analysis["metadata"]["repos_analyzed"] == 1
    assert len(analysis["repositories"]) == 1
    assert analysis["repositories"][0]["name"] == "repo1"
    assert analysis["cross_repo_analysis"]["total_components"] == 1
    assert analysis["cross_repo_analysis"]["total_vulnerabilities"] == 1
    assert analysis["cross_repo_analysis"]["total_codeql_issues"] == 1
    assert analysis["cross_repo_analysis"]["total_cicd_findings"] == 1

    validation = analysis["metadata"]["validation"]
    assert any("Invalid SBOM file" in warning for warning in validation["warnings"])
    assert str(invalid_sbom_file) in validation["invalid_files"]
