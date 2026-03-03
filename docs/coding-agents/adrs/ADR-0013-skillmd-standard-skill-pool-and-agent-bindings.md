# ADR-0013: SKILL.md Standard, Skill Pool, and Agent Binding Separation

- Status: Accepted
- Date: 2026-03-03
- Decision IDs: D096, D097, D098, D099, D100

## Context

aivp needs first-class interoperability with the open `SKILL.md` format so users can import reusable skills instead of rewriting tool interfaces per agent. At the same time, agent YAML should remain focused on goals and safety constraints, not redefining skill contracts.

## Decision

- Adopt `SKILL.md` as a first-class skill definition and import standard.
- Require machine-readable frontmatter in `SKILL.md` for enforceable contract fields (skill id, version, inputs, outputs, permission scope, risk metadata, execution hints).
- Treat the Markdown body in `SKILL.md` as agent guidance/context, not as the sole enforcement source.
- Maintain a global skill pool registry populated from imported `SKILL.md` skills.
- Separate agent-level config from skill definition:
  - skill pool contains canonical skill contracts,
  - agent YAML contains only `skill_bindings` (alias + optional argument constraints/overrides).
- Keep agent binding `fixed` argument maps optional by default, allowing users to tighten some/all arguments for safer mini-agents when desired.
- Support importing skills from local paths and Git sources with provenance metadata and hash pinning.
- Block activation when an agent binding references a missing/incompatible skill from the pool.
- Include resolved skill id/version/hash in immutable run snapshots.

## Consequences

- Skill authoring and sharing become portable and interoperable.
- Agent YAML is smaller and less repetitive.
- Safety enforcement stays server-side through skill contracts, policy checks, and executor validation.
- Imported skill updates become auditable through provenance and hash pinning.

## Alternatives Considered

- Continue using only Python-native skill contracts with no `SKILL.md` import path.
- Allow agents to redefine skill argument contracts inline in each agent YAML.
- Treat `SKILL.md` as documentation-only with no machine validation.
