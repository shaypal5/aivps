# ADR-0011: Packaging, Platform Support, and Extensibility

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D014, D023, D035, D054, D055, D062, D086, D087, D094, D095

## Context

The project needs fast iteration for v1 while preserving a path to stronger ecosystem controls and extensibility.

## Decision

- Keep v1 distribution pip/CLI-first.
- Maintain local file workflows plus Git-based skill/template distribution.
- Pin skills and templates with lockfile/hash metadata.
- Require provenance metadata including source, version/hash, license, and permission scope.
- Support explicit upgrade workflows with preflight checks and rollback snapshots.
- Support single-user mode in v1, with multi-profile isolation deferred.
- Support last 2-3 stable Python versions and lock runtime dependencies.
- Provide stable and opt-in beta release channels.
- Expose a versioned plugin API with capability flags.

## Consequences

- v1 remains lightweight and easy to adopt for Python users.
- Supply-chain and provenance posture is stronger than ad hoc imports.
- Extension growth is possible without freezing internal APIs prematurely.

## Alternatives Considered

- App-bundle-only release strategy.
- No lockfiles or provenance metadata.
- Unstable internal-only plugin surfaces indefinitely.
