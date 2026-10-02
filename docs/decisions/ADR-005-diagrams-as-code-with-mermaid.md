# ADR-005: Diagrams as Code With Mermaid

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

Architecture diagrams exported as images from drawing tools drift from the text, cannot be reviewed as diffs and
need the original tool to edit.

## Decision

All diagrams are Mermaid blocks embedded in Markdown, which GitHub renders natively. CI renders every diagram
with `@mermaid-js/mermaid-cli` and fails on syntax errors. Only widely supported diagram types are used
(`flowchart`, `sequenceDiagram`, `erDiagram`, `stateDiagram-v2`).

## Alternatives Considered

- **PlantUML** — more expressive, but not rendered natively by GitHub.
- **Images from a drawing tool** — best visual control, but not diffable and frequently stale.
- **C4 via Structurizr** — excellent for real architecture repositories, heavier than needed here.

## Trade-offs

Mermaid's layout control is limited; large diagrams can become cluttered. Designs therefore prefer several small
diagrams (request path, async path, data model) over one large one.

## Consequences

- Diagrams are reviewed in pull requests like any other text.
- Newer Mermaid syntax that GitHub has not yet adopted is avoided.
