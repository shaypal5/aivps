# aivp

`aivp` is a local-first mini-agent framework for defining narrow, safety-focused "AI VPs" using YAML.

## Current State

This repository currently contains:
- v1 architecture and ADR documentation under `docs/coding-agents/`
- an implementation roadmap
- initial Python and repository scaffolding

## Quick Start

1. Create a virtual environment.
2. Install editable package:
   - `pip install -e .`
3. Run scaffold health check:
   - `aivp doctor`

## Repository Layout

- `src/aivp/` Python package scaffold
- `config/` schemas and migrations
- `agents/templates/` starter YAML templates
- `skills/builtin/` built-in skill placeholders
- `runtime/` local runtime data directories
- `docs/coding-agents/` architecture, ADRs, roadmap

## Design Docs

- [System Design](docs/coding-agents/aivp-v1-system-design.md)
- [ADR Index](docs/coding-agents/adrs/README.md)
- [Implementation Roadmap](docs/coding-agents/implementation-roadmap.md)
