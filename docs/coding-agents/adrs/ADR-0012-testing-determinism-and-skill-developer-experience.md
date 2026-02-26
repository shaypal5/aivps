# ADR-0012: Testing, Determinism, and Skill Developer Experience

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D024, D043, D073, D085, D088

## Context

The platform depends on external APIs and time-based triggers, so deterministic testing and safe previews are required to prevent accidental side effects during development.

## Decision

- Provide dry-run mode with side-effect mocks and preview diffs.
- Provide deterministic test mode with virtual clock, mocked connectors, and replay fixtures.
- Provide typed SDK, scaffold command, and local harness for custom skill development.
- Ship curated versioned starter templates to reduce configuration errors.
- Do not require mandatory skill tests in v1.
- Track mandatory contract tests for mutating skills as a planned future change.

## Consequences

- Developers can test agents and skills safely before execution against real systems.
- Deterministic replay improves debuggability for schedule-driven behavior.
- v1 onboarding remains pragmatic while preserving a path to stricter quality gates.

## Alternatives Considered

- No deterministic mode.
- Tests required for all skills in v1.
- Docs-only custom skill developer workflow.

