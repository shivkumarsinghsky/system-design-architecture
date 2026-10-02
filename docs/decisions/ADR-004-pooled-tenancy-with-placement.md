# ADR-004: Pooled Tenancy With a Placement Table

- **Status:** Accepted
- **Date:** 2026-10-01
- **Applies to:** [Multi-Tenant SaaS](../designs/11-multi-tenant-saas.md), [Enterprise AI Platform](../designs/12-enterprise-ai-platform.md)

## Context

B2B SaaS tenants vary in size by four orders of magnitude. Isolation requirements also vary: most tenants accept
logical isolation, some contractually require dedicated infrastructure.

## Decision

Default to a **shared database, shared schema** model with a `tenant_id` column on every tenant-owned table and
PostgreSQL **row-level security** as a second line of defence. Introduce a **placement table** mapping each
tenant to a database cluster (and optional schema) so individual tenants can be moved to dedicated
infrastructure without code changes.

## Alternatives Considered

- **Database per tenant for everyone** — strongest isolation, but cost and operational overhead are
  unjustifiable for small tenants, and fleet-wide migrations become a project of their own.
- **Schema per tenant** — middle ground, but database catalogues degrade with thousands of schemas and
  migrations still multiply.
- **Shared schema without RLS** — simplest, but isolation then depends entirely on every query being correct.

## Trade-offs

Pooled infrastructure makes per-tenant restore harder (restore to the side, copy by tenant id) and creates
noisy-neighbour risk, mitigated with per-tenant quotas and fair scheduling.

## Consequences

- Every service resolves its connection through placement (cached).
- Isolation tests that attempt cross-tenant access are part of CI.
- Moving a tenant between tiers is an operational runbook, not a code change.
