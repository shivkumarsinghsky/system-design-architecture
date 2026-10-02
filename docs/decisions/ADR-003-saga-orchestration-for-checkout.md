# ADR-003: Orchestrated Saga for Multi-Service Checkout

- **Status:** Accepted
- **Date:** 2026-10-01
- **Applies to:** [E-Commerce](../designs/10-e-commerce.md); the same reasoning is reused wherever a business
  process spans several services that each own their data.

## Context

Checkout must reserve inventory, authorise payment and create an order. Each step belongs to a different service
with its own database. A two-phase commit across services (and an external payment provider) is not available and
would couple availability of all participants.

## Decision

Use a **saga** coordinated by a dedicated **orchestrator** that issues commands, records saga state durably,
and runs compensating actions (release reservation, void authorisation) on failure. Every command carries an
idempotency key derived from the checkout id.

## Alternatives Considered

- **Choreography** (each service reacts to the previous service's event) — lower coupling, but the checkout flow
  becomes implicit and spread across services; answering "where is this checkout stuck?" requires correlating
  several logs.
- **Two-phase commit** — strong atomicity, but blocking, not supported by the payment provider, and couples the
  availability of every participant.
- **Single service owning everything** — simplest consistency, but merges domains with different scaling and
  change rates.

## Trade-offs

The orchestrator is a critical component and must itself be highly available and idempotent. Intermediate states
are visible (stock reserved but not yet sold), which the domain must tolerate.

## Consequences

- Saga state is queryable for support and observability.
- Each participant exposes explicit compensating operations.
- Timeouts on uncertain steps (payment) are resolved by querying the participant, not by assuming failure.
