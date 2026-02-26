# aivp v1 Scope and Non-Goals

Status: Approved baseline for v1 delivery
Date: 2026-02-26
Primary reference: ADR-0001

## 1. Scope Statement

aivp v1 is a local-first, single-user framework for defining and running narrowly scoped AI agents ("AI VPs") with least-privilege, policy-enforced execution boundaries.

## 2. In Scope (v1)

- Local daemon runtime on user laptops, with macOS-first focus and Linux close second.
- YAML-first agent configuration with schema versioning and migration path.
- Capability-secure skill execution through a central non-agentic executor.
- Policy enforcement with deny-wins precedence and risk-based approval controls.
- Scheduling + event-trigger workflows with bounded catch-up and replay support.
- Structured local observability (runs, steps, skill calls, errors) and audit export.
- Budget/quota controls and policy-based model routing.
- CLI-first developer/operator workflow.

## 3. Out of Scope (v1)

- Multi-user collaborative operation.
- Cloud-hosted control plane as a core deployment target.
- Broad personal-assistant behavior with open-ended permissions.
- Mandatory enterprise controls (for example: mandatory DB encryption, mandatory OTel).
- Full marketplace automation and auto-update by default.

## 4. Explicit Non-Goals

- Not a general-purpose autonomous assistant with unrestricted tool access.
- Not a replacement for enterprise orchestration platforms.
- Not a guarantee of exactly-once effects across external provider APIs.
- Not a framework that trusts prompt instructions as the sole permission boundary.

## 5. Deferred Post-v1 Features (Tracked)

- Multi-profile isolation on one machine (post-v1 target, see ADR-0011 / D054).
- macOS app bundle and launch-agent packaging (post-v1 target, see ADR-0011 / D055).

Tracking issues:
- #22 post-v1: multi-profile isolation
- #23 post-v1: macOS app bundle packaging

## 6. Acceptance Criteria Mapping for Issue #1

- v1 scope doc (in/out): covered by sections 1-3.
- explicit non-goals list: covered by section 4.
- deferred features list tracked as post-v1: covered by section 5 and linked issues.
