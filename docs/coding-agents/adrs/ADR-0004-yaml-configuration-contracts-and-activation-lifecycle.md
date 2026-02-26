# ADR-0004: YAML Configuration, Contracts, and Activation Lifecycle

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D003, D004, D011, D018, D019, D036, D042, D046, D047, D051, D061, D076, D077

## Context

The product is YAML-first for users, but must stay safe and evolvable over time. Config changes should not silently widen permissions or destabilize running agents.

## Decision

- Use declarative YAML step graphs as the primary agent workflow model.
- Require schema versioning and migration tooling.
- Use strict validation by default with optional dev-mode leniency.
- Support per-agent timezone configuration.
- Support YAML include/import modularity.
- Use versioned prompt artifacts pinned per run.
- Enforce structured outputs via schema validation with repair retries.
- Use semver-style compatibility with deprecation windows and migration hints.
- Capture immutable per-run snapshots of config, prompt, skill, and policy hashes.
- Apply draft -> validate -> activate workflow with rollback on invalid changes.
- Block activation when contract changes break compatibility or widen permissions unexpectedly.
- Define skill contracts using typed Python models with JSON Schema export.

## Consequences

- Users retain YAML ergonomics while the runtime remains strongly validated.
- Migrations and compatibility checks reduce config drift and accidental breakage.
- Auditing and reproducibility improve through run snapshots and pinned artifacts.

## Alternatives Considered

- Free-form configs with best-effort runtime checks.
- Immediate live mutation without staged activation.
- Unversioned prompts and contracts.
