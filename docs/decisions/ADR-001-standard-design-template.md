# ADR-001: Standard Template for Every Design

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

System design write-ups tend to drift: one covers caching in depth and skips security, another jumps to a
database choice before stating requirements. Readers comparing designs need to find the same information in the
same place.

## Decision

Every document in `docs/designs/` uses the same top-level headings, in this order: Requirements, Functional
Requirements, Non-Functional Requirements, Capacity Estimation, High-Level Architecture, API Design, Data Model,
Caching, Messaging, Scaling, Reliability, Security, Observability, Trade-offs. CI enforces the presence and
order of these headings (`scripts/check_design_structure.py`).

## Alternatives Considered

- **Free-form documents** — more natural to write, but inconsistent and easy to leave gaps.
- **A longer template** (cost, compliance, migration plan) — valuable for real projects, but too heavy for
  reference designs whose purpose is to illustrate architecture trade-offs.

## Trade-offs

A fixed template sometimes forces a short section ("Messaging: not needed on the read path") where a free-form
document would omit it. That is accepted: an explicit "not needed, because…" is itself useful information.

## Consequences

- New designs are quick to review because gaps are visible.
- The structure check runs in CI; a design missing a section fails the build.
