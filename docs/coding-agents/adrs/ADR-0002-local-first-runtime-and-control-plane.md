# ADR-0002: Local-First Runtime and Control Plane

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D001, D016, D026, D027, D028, D029, D030, D039, D056, D057, D078

## Context

The system must run robustly on laptops that sleep, wake, and disconnect frequently. We need a control plane that is resilient locally while keeping execution isolated and manageable.

## Decision

- Run a background daemon locally, with optional auto-start on login.
- Use a persisted local event bus with versioned event schemas.
- Use a single SQLite database (WAL) as the primary persistence backend in v1.
- Execute each agent run in subprocesses by default.
- Support per-skill or per-provider virtual environment isolation where needed.
- Use per-agent scoped memory by default, with optional shared spaces.
- Default to non-overlapping runs (single-flight), configurable per agent.
- Use wall clock scheduling with monotonic guardrails for drift/sleep recovery.
- Enforce revision checks and locks for config edits.
- Apply global and per-run runtime resource caps.

## Consequences

- Local-first reliability is improved without requiring external infrastructure.
- Fault isolation is stronger than single-process agent execution.
- Operational behavior remains predictable across sleep/wake cycles.
- SQLite remains a practical v1 choice with minimal deployment burden.

## Alternatives Considered

- Single-process async-only execution for all runs.
- Multiple domain-specific databases in v1.
- Server-first hosted architecture.

