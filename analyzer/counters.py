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
