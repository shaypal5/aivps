# ADR-0001: Product Positioning and Scope

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D013, D054, D055

## Context

aivp is intended as a local-first framework for narrowly scoped "AI VP" agents with stronger safety properties than broad personal assistants. We need clear product boundaries for v1 so architecture and UX choices remain coherent.

## Decision

- Position aivp externally as a task-bounded local automation OS.
- Design internally as a capability-secure agent runtime.
- Ship v1 as single-user and pip/CLI-first.
- Keep multi-profile support and macOS app packaging as future enhancements.

## Consequences

- Architecture and docs consistently optimize for local laptop operation and least privilege.
- Control plane complexity is reduced in v1 by avoiding multi-profile and desktop bundle concerns.
- Security expectations are explicit: capabilities and policy are core, not optional.

## Alternatives Considered

- Broad personal assistant framing with wider default permissions.
- Multi-user or collaborative design in v1.
- App-bundle-first distribution in v1.

