from __future__ import annotations

from collections import Counter
from typing import Any


def count_by_field(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        value = item.get(field)
        key = str(value) if value not in (None, "") else "unknown"
        counter[key] += 1
    return dict(counter)


def top_n_by_field(items: list[dict[str, Any]], field: str, n: int = 10) -> list[dict[str, Any]]:
    counts = count_by_field(items, field)
    sorted_items = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
    return [{"value": key, "count": count} for key, count in sorted_items[:n]]


def severity_distribution(vulnerabilities: list[dict[str, Any]]) -> dict[str, int]:
    return count_by_field(vulnerabilities, "severity")


def top_codeql_rules(issues: list[dict[str, Any]], n: int = 10) -> list[dict[str, Any]]:
    return top_n_by_field(issues, "rule_id", n)


def top_codeql_files(issues: list[dict[str, Any]], n: int = 10) -> list[dict[str, Any]]:
    return top_n_by_field(issues, "file", n)


def count_true_field(items: list[dict[str, Any]], field: str) -> int:
    return sum(1 for item in items if item.get(field) is True)


def common_weakness_ranking(vulnerabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    ignored_values = {"", "unknown", "none", "null"}

    for vulnerability in vulnerabilities:
        value = vulnerability.get("cwe")
        if value is None:
            continue
        cwe = str(value).strip()
        if cwe.lower() in ignored_values:
            continue
        counter[cwe] += 1

    return [
        {"cwe": cwe, "count": count}
        for cwe, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]
