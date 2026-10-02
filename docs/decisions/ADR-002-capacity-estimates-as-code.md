# ADR-002: Capacity Estimates Generated From Code

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

Back-of-the-envelope numbers are usually calculated by hand and pasted into documents. Hand arithmetic contains
mistakes, assumptions are hidden, and when an assumption changes the numbers are rarely updated everywhere.

## Decision

Capacity assumptions live in `tools/capacity/scenarios.py` as typed `Workload` objects. A small, tested model
(`tools/capacity/model.py`) derives QPS, storage and bandwidth. Each design embeds a generated table between
`<!-- capacity:<key>:start -->` / `end` markers; `scripts/sync_capacity_tables.py` regenerates them and CI fails
if a table is out of date.

## Alternatives Considered

- **Spreadsheet per design** — familiar, but not reviewable in a pull request and not testable.
- **Hand-written tables** — zero tooling, but error-prone and silently stale.
- **A full simulation (queueing models)** — more accurate, but the purpose is order-of-magnitude reasoning.

## Trade-offs

The model is deliberately simple (uniform per-user rates, single peak factor). It does not capture diurnal
curves, cache hit ratios or fan-out amplification; those are discussed in prose where they matter.

## Consequences

- Assumptions are explicit and can be challenged in review by changing one number.
- The repository gains a Python dependency for contributors (standard library only at runtime; pytest for tests).
