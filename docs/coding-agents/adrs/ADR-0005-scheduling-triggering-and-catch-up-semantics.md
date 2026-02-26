# ADR-0005: Scheduling, Triggering, and Catch-Up Semantics

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D006, D017, D040, D049, D071, D072

## Context

Laptop-first systems miss time windows due to sleep, shutdown, and offline periods. Scheduling must recover safely without unbounded replay or duplicate side effects.

## Decision

- Use at-least-once delivery semantics with idempotency keys.
- Support schedule triggers and event predicates in YAML.
- Apply bounded catch-up windows and bounded backlog drain rates.
- Replay missed windows oldest-first.
- Use stale-run policies with TTL and freshness cutoff behavior.

## Consequences

- Missed work is recoverable while limiting overload bursts after downtime.
- Replay ordering is predictable and easier to reason about.
- Correctness depends on robust idempotency for mutating actions.

## Alternatives Considered

- At-most-once delivery with dropped missed windows.
- Execute entire backlog immediately after restart.
- Newest-first catch-up.
