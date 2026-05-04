from pathlib import Path

from analyzer.validators import (
    validate_cicd,
    validate_codeql,
    validate_codeql_normalized,
    validate_grype,
    validate_sbom,
)


def test_validate_sbom_invalid_missing_artifacts_collects_warning_and_file() -> None:
    path = Path("data/results/sboms/repo_sbom.json")
    result = validate_sbom({}, path)
    assert result.valid is False
    assert path.as_posix() in result.invalid_files
    assert result.warnings


def test_validate_grype_valid_matches_list() -> None:
    result = validate_grype({"matches": []}, Path("x.json"))
    assert result.valid is True
    assert result.warnings == []
    assert result.invalid_files == []


def test_validate_codeql_invalid_runs_type() -> None:
    result = validate_codeql({"runs": {}}, Path("a.sarif"))
    assert result.valid is False
    assert result.invalid_files == ["a.sarif"]


def test_validate_codeql_normalized_accepts_findings_results_or_runs() -> None:
    assert validate_codeql_normalized({"findings": []}, Path("f.json")).valid is True
    assert validate_codeql_normalized({"results": []}, Path("r.json")).valid is True
    assert validate_codeql_normalized({"runs": []}, Path("s.sarif")).valid is True


def test_validate_codeql_normalized_invalid_structure() -> None:
    result = validate_codeql_normalized({"foo": "bar"}, Path("bad.json"))
    assert result.valid is False
    assert result.warnings
    assert result.invalid_files == ["bad.json"]


def test_validate_cicd_invalid_missing_keys() -> None:
    result = validate_cicd({"repo": "r", "findings": []}, Path("cicd.json"))
    assert result.valid is False
    assert result.warnings
    assert result.invalid_files == ["cicd.json"]
