# ADR-0007: Budgets, Quotas, and LLM Routing

- Status: Accepted
- Date: 2026-02-26
- Decision IDs: D015, D020, D048, D070, D075, D092

## Context

Multiple agents compete for constrained API and LLM budgets. The system must enforce limits, prioritize important work, and still keep configuration simple for most users.

## Decision

- Use policy-driven LLM routing with fallback; allow fixed-per-agent model selection.
- Use priority queues plus token buckets with anti-starvation aging.
- Support hierarchical budgets at provider, skill, and agent levels.
- Keep provider-level budgets easy and first-class for typical users.
- On budget exhaustion, degrade by priority instead of hard stopping everything.
- Use least-context defaults with per-step context allowlists.
- Support optional per-agent SLO targets and degrade behavior.

## Consequences

- Critical agents can continue during quota pressure.
- Cost and performance tradeoffs are explicit and tunable.
- Default UX remains manageable even with advanced budget hierarchy available.

## Alternatives Considered

- Single flat quota model only.
- Strict hard-stop behavior for all agents at cap hit.
- One-model-for-all routing.

