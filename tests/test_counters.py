from analyzer.counters import common_weakness_ranking, count_by_field


def test_count_by_field_maps_empty_and_none_to_unknown() -> None:
    items = [{"severity": "high"}, {"severity": ""}, {"severity": None}, {}]
    counts = count_by_field(items, "severity")
    assert counts == {"high": 1, "unknown": 3}


def test_common_weakness_ranking_ignores_null_empty_unknown() -> None:
    vulnerabilities = [
        {"cwe": "CWE-79"},
        {"cwe": "CWE-79"},
        {"cwe": "Unknown"},
        {"cwe": "unknown"},
        {"cwe": ""},
        {"cwe": None},
        {"cwe": " null "},
    ]

    ranking = common_weakness_ranking(vulnerabilities)
    assert ranking == [{"cwe": "CWE-79", "count": 2}]
