# ADR-0008: Persistence, Observability, Audit, and Retention

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D012, D025, D052, D059, D063, D074, D084, D093

## Context

To operate safely, aivp needs strong local observability and auditability while minimizing sensitive data exposure and storage growth.

## Decision

- Persist runtime state and telemetry locally with structured traces.
- Track run, step, and skill-call traces with correlation identifiers.
- Enable prompt and response capture by default with redaction controls.
- Use retention policies and field-level redaction as defaults.
- Support optional local DB encryption.
- Optimize dashboards via materialized summaries and lazy drill-down.
- Provide signed tamper-evident audit bundles plus plain JSON/CSV exports.
- Manage artifact lifecycle with retention tiers, dedupe/compression, and garbage collection.
- Keep OpenTelemetry export as a future integration.

## Consequences

- Local debugging and audit workflows are practical without external tooling.
- Data growth remains manageable with explicit retention and artifact GC.
- Privacy posture is improved by default redaction and optional encryption.

## Alternatives Considered

- Logs-only observability.
- No signed audit mechanism.
- Unlimited retention of all payloads.
