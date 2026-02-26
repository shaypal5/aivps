# ADR-0003: Capability-Secure Skill Execution and Authorization

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D002, D008, D022, D037, D038, D044, D045, D060, D066, D067, D082, D083, D090, D091

## Context

aivp requires strict least-privilege behavior. Agents should not directly hold broad secrets or execute unconstrained external actions. Authorization must be enforceable beyond prompt instructions.

## Decision

- Enforce permissions with capability checks at runtime, not prompt-only controls.
- Route all skill execution through a central non-agentic server executor.
- Use a policy DSL for authorization and approval rules.
- Apply explicit deny-wins precedence across policy scopes.
- Trigger plan/preview flow for high-risk actions by policy.
- Support per-agent no-ask mode when explicitly configured.
- Enforce deny-by-default network egress with explicit allowlists.
- Use field-level sensitivity tags and redaction in logs and UI.
- Resolve secrets just-in-time in the executor context, scoped per skill call.
- Validate skill parameters pre-execution with declarative constraints.
- Authorize every tool or skill call before execution.
- Minimize and filter data before LLM prompt assembly.
- Require extra safeguards for irreversible actions.
- Support explicit ABSTAIN outcomes.

## Consequences

- Stronger security posture and safer defaults for local automation.
- Agent definitions remain expressive while constrained.
- Centralized authorization makes audits and incident response simpler.

## Alternatives Considered

- Prompt-only permission enforcement.
- Direct in-process agent access to integration libraries.
- Allow-by-default outbound network model.

