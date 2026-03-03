# SKILL.md Support and Binding Model

Status: Design baseline
Date: 2026-03-03
Related ADR: [ADR-0013](./adrs/ADR-0013-skillmd-standard-skill-pool-and-agent-bindings.md)

## 1. Scope

This document defines how aivp fully supports `SKILL.md` as an import standard while keeping agent YAML focused on goals and optional safety constraints.

## 2. Separation Model

- Skill pool:
  - canonical imported skills from `SKILL.md`
  - each skill has id/version/hash/provenance
  - shared across many agents
- Agent config:
  - references skills only through `skill_bindings`
  - may optionally fix a subset of skill arguments
  - does not redefine full skill interface

## 3. Import Workflow

1. User imports a local path or Git source.
2. Runtime discovers `SKILL.md` files.
3. `SKILL.md` frontmatter is validated against contract schema.
4. Skill is registered in pool with id/version/hash/provenance.
5. Lockfile is updated.
6. Agent activation validates all bindings against pool contracts.

## 4. Skill Pool Manifest Shape

```yaml
schema_version: skill_pool.v1
imports:
  - kind: local
    path: ./skills/imported
  - kind: git
    url: https://github.com/example/skill-pack
    ref: v1.4.2
    subpath: skills
registry:
  - id: gmail.inbox_label_delta_scan
    version: 1.2.0
    source: local
    status: active
```

## 5. SKILL.md Contract Shape

`SKILL.md` must include machine-readable frontmatter and may include additional human-readable instructions in Markdown body.

```md
---
schema_version: skill.v1
id: gmail.inbox_label_delta_scan
version: 1.2.0
summary: Scan inbox emails by source label and exclude processed label.
inputs:
  type: object
  required: [label_name, exclude_label_names]
  properties:
    label_name: { type: string }
    exclude_label_names:
      type: array
      items: { type: string }
    mailbox:
      type: string
      enum: [inbox_only]
      default: inbox_only
    lookback_days:
      type: integer
      minimum: 1
      maximum: 3650
outputs:
  type: object
  properties:
    emails:
      type: array
permissions:
  gmail:
    mailbox: inbox_only
risk:
  level: medium
---

# Usage Notes
This section is guidance for planning/reasoning, not the only enforcement source.
```

## 6. Agent Binding Shape

```yaml
skill_bindings:
  - as: find_candidate_emails
    use: gmail.inbox_label_delta_scan
    fixed:
      label_name: "Consulting Expenses"
      exclude_label_names: ["vp_expenses_processed"]
      mailbox: inbox_only
      lookback_days: 90
```

`fixed` is optional and may include any subset of input fields.

## 7. Runtime Rules

- The executor validates final arguments against imported skill contract schema.
- Policy/authorization checks run before each skill call.
- Activation fails if `use` points to missing skill id or incompatible version/contract.
- Run snapshots include bound skill id/version/hash.
