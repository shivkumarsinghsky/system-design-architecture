#!/usr/bin/env python3
"""Enforce ADR-001: every design document has the standard sections, in order."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "Requirements",
    "Functional Requirements",
    "Non-Functional Requirements",
    "Capacity Estimation",
    "High-Level Architecture",
    "API Design",
    "Data Model",
    "Caching",
    "Messaging",
    "Scaling",
    "Reliability",
    "Security",
    "Observability",
    "Trade-offs",
]
H2 = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
DISCLAIMER = "Reference system design"


def check(doc: Path) -> list[str]:
    text = doc.read_text(encoding="utf-8")
    problems: list[str] = []
    headings = [h for h in H2.findall(text) if h in REQUIRED]
    missing = [h for h in REQUIRED if h not in headings]
    if missing:
        problems.append(f"missing sections: {', '.join(missing)}")
    elif headings != REQUIRED:
        problems.append("sections out of order")
    if DISCLAIMER not in text.split("\n## ", 1)[0]:
        problems.append("missing 'Reference system design' disclaimer before the first section")
    return problems


def main() -> int:
    docs = sorted((ROOT / "docs" / "designs").glob("*.md"))
    failed = 0
    for doc in docs:
        for p in check(doc):
            print(f"{doc.name}: {p}")
            failed += 1
    print(f"checked {len(docs)} designs, {failed} problems")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
