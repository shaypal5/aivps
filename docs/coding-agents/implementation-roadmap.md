# aivp v1 Implementation Roadmap

Status: Proposed execution plan
Date: 2026-02-26
Inputs: ADR-0001 through ADR-0012

## 1. Scope

This roadmap converts accepted ADRs into build-ready epics and issue-sized work items for v1.

## 2. Milestone Plan

## M0 - Repository Foundations

- EPIC-01 Product scope and contribution conventions
- EPIC-02 Runtime skeleton and project structure
- EPIC-11 Platform and packaging baseline

Exit criteria:
- Project boots as local daemon in development mode.
- Core directories and module boundaries are stable.
- Python/version/dependency policies are enforceable in CI.

## M1 - Secure Config and Policy Core

- EPIC-03 Capability-secure execution path
- EPIC-04 Config/contracts/activation lifecycle

Exit criteria:
- Agents can be validated, activated, and denied safely by policy.
- Skill execution can only happen through the central executor.

## M2 - Scheduling and Reliable Execution

- EPIC-05 Scheduling, triggers, catch-up
- EPIC-06 Reliability, idempotency, failure recovery

Exit criteria:
- Missed windows replay safely.
- Runs are bounded, retryable, and auditable with dead-letter handling.

## M3 - Quotas, Routing, and Data Plane

- EPIC-07 Budgets, quotas, model routing
- EPIC-08 Persistence, traces, retention, audit
- EPIC-09 Secrets/connectors/artifacts

Exit criteria:
- Budget enforcement and degradation policies are active.
- Structured traces and signed audit export are available.
- Connectors run through scoped secrets and artifact handles.

## M4 - UX and Developer Enablement

- EPIC-10 Dashboard/API/op controls
- EPIC-12 Testing, determinism, skill DX

Exit criteria:
- Users can operate system from UI/TUI/API.
- Dry-run + deterministic test harness supports safe development.

## 3. Epic Backlog

## EPIC-01 Product Scope and Governance (ADR-0001)

Goal:
- Lock v1 boundaries and success criteria for local, single-user, least-privilege operation.

Issues:
1. Create product spec summary and non-goals document.
2. Add architectural guardrails to `CONTRIBUTING.md`.
3. Add ADR usage policy for all major changes.
4. Add v1 feature gate list (deferred items: multi-profile, macOS bundle).

Acceptance criteria:
- All v1 PRs reference one ADR or explicit "no ADR required" rationale.
- Deferred features are labeled and excluded from v1 milestone.

## EPIC-02 Local Runtime and Control Plane Skeleton (ADR-0002)

Goal:
- Implement daemon, event bus, subprocess run model, and runtime boundaries.

Issues:
1. Create core packages: `aivp.server`, `aivp.runtime`, `aivp.bus`, `aivp.scheduler`.
2. Implement daemon startup/shutdown and PID lock.
3. Implement SQLite WAL bootstrap and migrations table.
4. Implement persisted event bus with versioned envelope.
5. Implement subprocess run launcher with resource caps.
6. Implement single-flight default lock for agent runs.
7. Add per-agent state store abstraction with optional shared namespace.

Acceptance criteria:
- Daemon can schedule and launch a no-op agent run end-to-end.
- Process recovery works after abrupt stop.
- Single-flight behavior is enforced by default.

## EPIC-03 Capability-Secure Skill Execution (ADR-0003)

Goal:
- Enforce least-privilege execution through centralized authorization and executor path.

Issues:
1. Implement policy DSL parser/evaluator.
2. Implement deny-wins precedence resolver.
3. Implement central non-agentic skill executor service.
4. Implement call authorization gate before every skill invocation.
5. Implement parameter constraint validator (enum/range/pattern/date).
6. Implement risk-triggered preview/approval workflow.
7. Implement ABSTAIN result contract.
8. Implement outbound egress allowlist checks.
9. Implement redaction pipeline for sensitive fields in logs/traces.

Acceptance criteria:
- Agent cannot call integration code directly.
- Unauthorized calls are denied with structured reasons.
- High-risk actions can require preview/approval by policy.

## EPIC-04 YAML Config, Contracts, Activation Lifecycle (ADR-0004)

Goal:
- Build strongly validated, versioned, and reversible configuration lifecycle.

Issues:
1. Define YAML schemas for agent, skill refs, triggers, policies.
2. Add `schema_version` enforcement and migration CLI.
3. Add YAML include/import loader with cycle detection.
4. Implement draft -> validate -> activate flow.
5. Implement rollback on invalid activation.
6. Add prompt artifact version pinning.
7. Add structured-output schemas and repair retry loop.
8. Implement compatibility checks on permission broadening/breaking contract changes.
9. Persist immutable run snapshots (config/prompt/skill/policy hashes).

Acceptance criteria:
- Invalid config never reaches active state.
- Activation produces deterministic versioned snapshot for each run.
- Compatibility gate blocks unsafe contract changes.

## EPIC-05 Scheduling, Triggering, Catch-Up (ADR-0005)

Goal:
- Execute schedule and event triggers with bounded replay and deterministic ordering.

Issues:
1. Implement schedule parser with per-agent timezone.
2. Implement event predicate DSL runtime.
3. Implement missed-window detection with oldest-first replay.
4. Implement bounded backlog drain controls and jitter.
5. Implement stale-run TTL/freshness cutoff rules.
6. Add at-least-once delivery acknowledgements.

Acceptance criteria:
- Sleep/wake scenarios recover missed runs within policy bounds.
- Replay order and drop behavior are transparent in run metadata.

## EPIC-06 Reliability, Idempotency, Recovery (ADR-0006)

Goal:
- Ensure safe retries, compensation behavior, incident controls, and replay tooling.

Issues:
1. Implement idempotency key framework for mutating steps.
2. Implement resource lease/lock manager for shared targets.
3. Implement retry/backoff/circuit-breaker policy engine.
4. Implement dead-letter queue and replay API.
5. Implement per-step and per-run timeout budget enforcement.
6. Implement saga compensation hooks for step groups.
7. Implement auto-remediation policies (pause/reduce/alert).
8. Implement incident controls (scoped pause, denylist, kill switch).
9. Implement provider-rate adaptation from 429 and response headers.
10. Implement filtered bulk replay with dry-run preview.

Acceptance criteria:
- Duplicate external side effects are prevented under retries/replays.
- Operators can replay failed workload safely.
- Incident controls can halt problematic workloads quickly.

## EPIC-07 Budgets, Quotas, and LLM Routing (ADR-0007)

Goal:
- Enforce spend and throughput constraints while preserving priority and quality.

Issues:
1. Implement hierarchical budget model (provider/skill/agent).
2. Implement provider-level-first configuration UX.
3. Implement priority scheduler with token buckets + anti-starvation aging.
4. Implement cap-hit degradation policy by priority.
5. Implement policy-based LLM routing with fallback.
6. Implement optional fixed-per-agent model override.
7. Implement per-step least-context allowlists and context budgeting.
8. Implement optional per-agent SLO configuration and degrade behavior.

Acceptance criteria:
- Budget limits are enforced deterministically at runtime.
- Low-priority agents defer before high-priority agents under scarcity.

## EPIC-08 Persistence, Observability, Audit, Retention (ADR-0008)

Goal:
- Provide operationally useful traces and auditability with privacy-aware defaults.

Issues:
1. Define SQLite schema for runs/events/steps/skill-calls/errors.
2. Implement correlation IDs across run -> step -> skill call.
3. Implement redacted prompt/response storage.
4. Implement retention policy engine and cleanup jobs.
5. Implement optional DB encryption support.
6. Implement materialized summary tables for dashboard views.
7. Implement signed audit export bundles.
8. Implement plain CSV/JSON export.
9. Implement artifact GC pipeline (retention tiers, dedupe/compression).
10. Add OpenTelemetry integration backlog item (future).

Acceptance criteria:
- Operators can trace any run from trigger through side effects.
- Audit exports are verifiable and privacy-safe by default.

## EPIC-09 Secrets, Connectors, Artifacts (ADR-0009)

Goal:
- Keep connector operations secure and reliable with explicit artifact access patterns.

Issues:
1. Implement keychain-backed secret provider.
2. Implement env/config secret ingestion with scope restrictions and warnings.
3. Implement just-in-time secret resolution in executor.
4. Implement connector health checks and token-expiry checks.
5. Implement artifact handle service with ACL + TTL.
6. Implement evidence-reference model in run outputs.
7. Implement signed connector/skill update ingestion workflow (approval required).
8. Implement configurable runtime storage paths for DB/log/artifact/backups.
9. Implement telemetry opt-in flow during onboarding.

Acceptance criteria:
- Agents do not receive broad secrets directly.
- Attachments are referenced via scoped handles, not prompt inlining.

## EPIC-10 Interfaces, Local API, Operations (ADR-0010)

Goal:
- Deliver safe and practical operations through web UI, TUI, and local API.

Issues:
1. Build local auth module (token sessions, scopes).
2. Implement localhost HTTP API for run control and status.
3. Build dashboard core pages (agents, runs, errors, signals, policies).
4. Build TUI parity for key operational actions.
5. Implement rule-based alerts (severity/channel/cooldown).
6. Implement backup/export and import/restore commands + UI hooks.
7. Implement guided setup wizard with starter template flow.

Acceptance criteria:
- All essential control operations exist in both API and at least one UI.
- Auth is enabled by default for local control surfaces.

## EPIC-11 Packaging, Platform, Extensibility (ADR-0011)

Goal:
- Stabilize runtime packaging and extension rules for v1 and near-term growth.

Issues:
1. Define supported Python versions and CI matrix.
2. Create dependency locking workflow for runtime and templates.
3. Implement skill/template lockfile with provenance fields.
4. Implement explicit upgrade command with preflight and rollback snapshot.
5. Implement release-channel config (stable/beta).
6. Define versioned plugin API and capability flags.
7. Add Git-based import path for skills/templates with hash pinning.
8. Add v1 boundary checks for single-user mode.
9. Add future issue for macOS bundle packaging.

Acceptance criteria:
- Reproducible installs are possible across supported Python versions.
- Provenance and pinning are enforced for imported assets.

## EPIC-12 Testing, Determinism, Skill DX (ADR-0012)

Goal:
- Enable safe development and reproducible debugging of agent behavior.

Issues:
1. Implement dry-run execution mode with side-effect mocks.
2. Implement deterministic test mode with virtual clock.
3. Implement connector mock interfaces and replay fixtures.
4. Build custom skill SDK types and scaffold CLI.
5. Build local harness for skill contract validation.
6. Provide curated starter templates (versioned).
7. Add future issue: mandatory contract tests for mutating skills.

Acceptance criteria:
- Developers can validate and preview an agent without real-world side effects.
- Time-based behavior is reproducible under deterministic tests.

## 4. Cross-Epic Dependency Order

1. EPIC-01 -> EPIC-02 -> EPIC-03 -> EPIC-04
2. EPIC-04 -> EPIC-05 -> EPIC-06
3. EPIC-03 + EPIC-06 -> EPIC-07 + EPIC-09
4. EPIC-02 + EPIC-08 -> EPIC-10
5. EPIC-11 and EPIC-12 can start early but finish after EPIC-04 baselines.

## 5. Suggested Initial GitHub Issues (First 20)

1. `roadmap: establish v1 scope and non-goals`
2. `runtime: daemon bootstrap and pid lock`
3. `storage: sqlite wal bootstrap and migration table`
4. `bus: persisted event envelope v1`
5. `runtime: subprocess run launcher with limits`
6. `runtime: single-flight default locking`
7. `policy: yaml dsl parser and evaluator`
8. `policy: deny-wins precedence engine`
9. `executor: central non-agentic skill execution service`
10. `executor: pre-exec parameter constraint validator`
11. `config: schema_version and migration cli`
12. `config: include/import loader with cycle detection`
13. `config: draft-validate-activate pipeline`
14. `config: compatibility gate for contract widening`
15. `scheduler: timezone-aware trigger engine`
16. `scheduler: bounded catch-up replay oldest-first`
17. `reliability: idempotency key framework`
18. `reliability: retry/backoff/circuit-breaker policy`
19. `reliability: dead-letter queue and replay api`
20. `security: egress allowlist enforcement`

## 6. Definition of Done (v1)

- All EPIC acceptance criteria met.
- Every mutating skill path has idempotency and policy enforcement.
- Catch-up, replay, and incident controls validated by deterministic tests.
- Budget and routing policies verified under constrained quota scenarios.
- Dashboard/TUI/API provide operational parity for core controls.
- Documentation includes:
  - system design,
  - ADR index and files,
  - operator runbook,
  - custom skill developer guide.
