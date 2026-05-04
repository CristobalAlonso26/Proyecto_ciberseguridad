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
    # grype: (2*4 + 4*1 + 1.5*2) / 3 = 5.0
    # codeql=0, cicd=0 → both components = 0
    # raw = 5.0 * 0.6 + 0 + 0 = 3.0
    assert risk_score_raw(vulns, 0, 0) == 3.0


def test_risk_score_raw_handles_invalid_risk_values() -> None:
    vulns = [
        {"severity": "High", "risk": "not-a-number"},
        {"severity": "Unknown", "risk": None},
    ]
    # Both vulns skipped → grype component = 0
    assert risk_score_raw(vulns, 0, 0) == 0.0


def test_risk_score_raw_empty_vulnerabilities_with_codeql_cicd() -> None:
    # grype: 0
    # codeql: log1p(10)*2 ≈ 4.80
    # cicd: log1p(3)*3 ≈ 4.16
    # raw = 0*0.6 + 4.80*0.2 + 4.16*0.2 ≈ 1.79
    assert risk_score_raw([], 10, 3) == 1.79


def test_risk_score_is_clamped_between_0_and_10() -> None:
    vulns = [{"severity": "Critical", "risk": 10}]
    # grype: 10*4 / 1 = 40 → raw = 40*0.6 = 24.0
    # risk_score = min(24.0, 10) = 10.0
    assert risk_score(vulns, 0, 0) == 10.0
