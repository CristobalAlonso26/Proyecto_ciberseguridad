from analyzer.metrics import risk_score, risk_score_raw, vulnerability_density


def test_vulnerability_density_with_zero_components_and_zero_vulns() -> None:
    assert vulnerability_density(0, 0) == 0.0


def test_vulnerability_density_with_zero_components_and_nonzero_vulns() -> None:
    assert vulnerability_density(3, 0) == 300.0


def test_vulnerability_density_normal_case() -> None:
    assert vulnerability_density(5, 20) == 25.0


def test_risk_score_raw_weighted_average_by_severity() -> None:
    vulns = [
        {"severity": "Critical", "risk": 2},
        {"severity": "Low", "risk": 4},
        {"severity": "Medium", "risk": 1.5},
    ]
    # (2*4 + 4*1 + 1.5*2) / 3 = 5
    assert risk_score_raw(vulns, total_codeql_issues=1000, total_cicd_findings=1000) == 5.0


def test_risk_score_raw_handles_invalid_risk_values() -> None:
    vulns = [
        {"severity": "High", "risk": "not-a-number"},
        {"severity": "Unknown", "risk": None},
    ]
    assert risk_score_raw(vulns, total_codeql_issues=0, total_cicd_findings=0) == 0.0


def test_risk_score_raw_empty_vulnerabilities() -> None:
    assert risk_score_raw([], total_codeql_issues=10, total_cicd_findings=3) == 0.0


def test_risk_score_is_clamped_between_0_and_10() -> None:
    vulns = [{"severity": "Critical", "risk": 10}]
    assert risk_score(vulns, total_codeql_issues=0, total_cicd_findings=0) == 10.0
