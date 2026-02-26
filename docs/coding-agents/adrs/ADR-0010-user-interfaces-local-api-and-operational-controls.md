# ADR-0010: User Interfaces, Local API, and Operational Controls

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D031, D032, D033, D034, D065

## Context

Users need safe and practical local controls for defining, monitoring, and pausing agents. Interfaces should support both direct usage and operational incident handling.

## Decision

- Provide local dashboard and TUI as primary operational interfaces.
- Enable localhost auth by default (optional to disable).
- Provide localhost HTTP API with token-based scoped authorization.
- Use rule-based alerting with severity, channel routing, and cooldown logic.
- Provide built-in backup and restore via signed export/import bundles.
- Provide a guided first-run setup flow with starter templates.

## Consequences

- Operational controls are available without external services.
- API and UI share the same local trust boundary model.
- Onboarding becomes faster and safer for new users.

## Alternatives Considered

- UI-only control model with no local API.
- No auth on local interfaces.
- Manual backup via file copies only.

