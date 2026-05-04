from analyzer.cicd_parser import normalize_repo_name, parse_cicd
from analyzer.codeql_parser import parse_codeql
from analyzer.grype_parser import parse_grype
from analyzer.sbom_parser import parse_sbom


def test_parse_sbom_counts_types_and_languages() -> None:
    data = {
        "artifacts": [
            {"type": "npm", "language": "JavaScript"},
            {"type": "deb", "language": "unknown"},
            {"type": "npm", "language": "JavaScript"},
        ]
    }
    parsed = parse_sbom(data)
    assert parsed["total_components"] == 3
    assert parsed["by_type"] == {"npm": 2, "deb": 1}
    assert parsed["by_language"] == {"JavaScript": 2, "unknown": 1}


def test_parse_grype_extracts_core_fields_and_fix_availability() -> None:
    data = {
        "matches": [
            {
                "vulnerability": {
                    "id": "CVE-2024-0001",
                    "severity": "High",
                    "risk": 7.3,
                    "cvss": [{"metrics": {"baseScore": 9.8}}],
                    "epss": [{"epss": 0.75}],
                    "cwes": [{"cwe": "CWE-79"}],
                    "fix": {"state": "fixed", "versions": ["2.0.0"]},
                },
                "artifact": {
                    "name": "requests",
                    "version": "1.0.0",
                    "type": "python",
                    "language": "python",
                    "locations": [{"path": "/src/requirements.txt"}],
                },
                "matchDetails": [{"fix": {"suggestedVersion": "2.0.1"}}],
            }
        ]
    }

    parsed = parse_grype(data)
    assert len(parsed) == 1
    item = parsed[0]
    assert item["id"] == "CVE-2024-0001"
    assert item["severity"] == "High"
    assert item["cvss_score"] == 9.8
    assert item["epss"] == 0.75
    assert item["cwe"] == "CWE-79"
    assert item["location"] == "/src/requirements.txt"
    assert item["fix_available"] is True
    assert item["fix_version"] == "2.0.1"


def test_parse_codeql_uses_result_level_and_fallback_to_rule_default() -> None:
    sarif = {
        "runs": [
            {
                "tool": {
                    "driver": {
                        "rules": [
                            {"id": "js/rule-a", "defaultConfiguration": {"level": "warning"}},
                            {"id": "js/rule-b", "defaultConfiguration": {"level": "error"}},
                        ]
                    }
                },
                "results": [
                    {
                        "ruleId": "js/rule-a",
                        "level": "note",
                        "message": {"text": "explicit level"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/a.js"},
                                    "region": {"startLine": 10, "startColumn": 2},
                                }
                            }
                        ],
                    },
                    {
                        "ruleId": "js/rule-b",
                        "message": {"text": "fallback to rule default"},
                        "locations": [],
                    },
                ],
            }
        ]
    }

    issues = parse_codeql(sarif)
    assert len(issues) == 2
    assert issues[0]["level"] == "note"
    assert issues[1]["level"] == "error"
    assert issues[0]["file"] == "src/a.js"
    assert issues[0]["line"] == 10


def test_parse_codeql_returns_unknown_level_without_rule_or_result_level() -> None:
    sarif = {"runs": [{"results": [{"message": {"text": "x"}}]}]}
    issues = parse_codeql(sarif)
    assert issues[0]["level"] == "unknown"


def test_parse_cicd_handles_invalid_structures_and_filters_empty_issues() -> None:
    data = {
        "workflows_scanned": -1,
        "findings": [
            {"workflow": "build.yml", "issues": ["unpinned action", "", None]},
            {"workflow": "deploy.yml", "issues": "not-a-list"},
        ],
    }
    parsed = parse_cicd(data)
    assert parsed["workflows_scanned"] == 0
    assert parsed["total_findings"] == 1
    assert parsed["items"] == [{"workflow": "build.yml", "issue": "unpinned action"}]


def test_normalize_repo_name_variants() -> None:
    assert normalize_repo_name("https://github.com/org/repo/") == "repo"
    assert normalize_repo_name("repo") == "repo"
    assert normalize_repo_name(None) == "unknown"
