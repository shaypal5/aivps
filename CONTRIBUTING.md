# Contributing

## Principles

- Keep `aivp` local-first.
- Prefer least-privilege and fail-closed behavior.
- Enforce policy and capability checks in code, not prompts.

## Architecture Process

- Major design changes must reference an ADR under `docs/coding-agents/adrs/`.
- If a change deviates from existing ADRs, update the ADR set in the same PR.
- Keep roadmap and design docs aligned with implementation changes.

## Development

1. Use Python 3.11-3.13.
2. Create a virtual environment.
3. Install editable dependencies with `pip install -e .`.
4. Run `aivp doctor` for local scaffold checks.

## Pull Requests

- Use focused PRs with clear scope.
- Include test/validation notes in PR description.
- For security-sensitive changes, include policy impact notes.
- For architecture-impacting changes, include an `ADR:` reference in the PR description.
- If no ADR applies, include `ADR: none (reason)` in the PR description.
