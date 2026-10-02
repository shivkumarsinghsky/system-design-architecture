"""The repository checks are part of the quality bar, so they are tested too."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


structure = load("check_design_structure")
links = load("check_links")


def test_every_design_follows_the_template():
    for doc in sorted((ROOT / "docs" / "designs").glob("*.md")):
        assert structure.check(doc) == [], doc.name


def test_missing_section_is_reported(tmp_path):
    sections = [h for h in structure.REQUIRED if h != "Caching"]
    body = "> Reference system design\n\n" + "\n".join(f"## {h}\n" for h in sections)
    doc = tmp_path / "bad.md"
    doc.write_text(body)
    assert structure.check(doc) == ["missing sections: Caching"]


def test_out_of_order_and_missing_disclaimer(tmp_path):
    order = list(reversed(structure.REQUIRED))
    doc = tmp_path / "bad.md"
    doc.write_text("\n".join(f"## {h}\n" for h in order))
    problems = structure.check(doc)
    assert "sections out of order" in problems
    assert any("disclaimer" in p for p in problems)


def test_slugify_matches_github_style():
    assert links.slugify("Non-Functional Requirements") == "non-functional-requirements"
    assert links.slugify("Caching `Redis` (L2)") == "caching-redis-l2"
