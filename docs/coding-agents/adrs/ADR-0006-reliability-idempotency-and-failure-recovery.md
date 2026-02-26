# ADR-0006: Reliability, Idempotency, and Failure Recovery

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D005, D007, D009, D021, D041, D053, D064, D079, D080

## Context

Agent runs touch external systems where transient errors, partial failures, and retries are expected. We need explicit semantics that prioritize correctness over throughput.

## Decision

- Require strong idempotency for mutating operations.
- Use resource locks or leases for shared mutable targets.
- Apply per-skill retry/backoff/circuit-breaker policies.
- Use dead-letter handling for persistent failures.
- Enforce per-step and per-run timeout budgets with kill escalation.
- Model multi-step side effects with saga compensation where possible.
- Use policy-based auto-remediation actions for repeated failures.
- Provide scoped incident controls: pause, denylist, kill switch.
- Adapt to provider rate-limit feedback dynamically.
- Support filtered bulk replay with preview and dry-run options.

## Consequences

- Runtime behavior is more predictable in the face of connector failures.
- Compensation and idempotency reduce duplicate or corrupted side effects.
- Operational controls support safer recovery during incidents.

## Alternatives Considered

- Best-effort retries without compensation model.
- Unlimited concurrency and no resource leases.
- Manual one-run-at-a-time replay only.

