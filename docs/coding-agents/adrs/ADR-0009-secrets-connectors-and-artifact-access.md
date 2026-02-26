# ADR-0009: Secrets, Connectors, and Artifact Access

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D010, D050, D058, D068, D069, D081, D089

## Context

Integration access must be secure and operationally reliable while preserving local-first usability. Artifacts and evidence need controlled access rather than direct data sprawl in prompts.

## Decision

- Use OS keychain as primary secrets backend.
- Allow env/config token injection where users choose, with clear scope expectations.
- Keep secrets primarily inside the server-side executor path, not broad agent context.
- Use structured evidence references in outputs rather than raw payload dumps.
- Use scoped artifact handles with TTL for attachment and binary access.
- Provide proactive connector health checks and token-expiry detection.
- Use signed update feeds with explicit user approval for integrations and skills.
- Keep data locations configurable for DB/logs/artifacts/backups.
- Prompt users for explicit telemetry opt-in during onboarding.

## Consequences

- Secret exposure risk is reduced while still allowing practical setup flows.
- Artifact handling is safer and more efficient than prompt inlining.
- Connector reliability improves with proactive health monitoring.

## Alternatives Considered

- Store all credentials in plain env files only.
- Inline attachment bytes directly into LLM prompts by default.
- Silent auto-update of integrations and skill packs.

