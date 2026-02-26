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

## Daemon Commands

- Start daemon loop (foreground):
  - `aivp daemon start --pid-file runtime/daemon.pid [--heartbeat-seconds N] [--max-heartbeats M]`
- Stop daemon:
  - `aivp daemon stop --pid-file runtime/daemon.pid`
- Restart daemon:
  - `aivp daemon restart --pid-file runtime/daemon.pid [--heartbeat-seconds N] [--max-heartbeats M]`

Notes:
- `daemon stop` is idempotent and returns success when the daemon is already stopped.
- `daemon start` returns a non-zero exit code when a daemon is already running for the same PID file.
- Use `aivp daemon --help` and subcommand `--help` for additional options.

## Database Commands

- Initialize runtime SQLite DB (WAL + schema state table):
  - `aivp db init --db-path runtime/db/aivp.sqlite3 --migration-version v1alpha1`

## Repository Layout

- `src/aivp/` Python package scaffold
- `config/` schemas and migrations
- `agents/templates/` starter YAML templates
- `skills/builtin/` built-in skill placeholders
- `runtime/` local runtime data directories
- `docs/coding-agents/` architecture, ADRs, roadmap

## Design Docs

- [System Design](docs/coding-agents/aivp-v1-system-design.md)
- [v1 Scope and Non-Goals](docs/coding-agents/v1-scope-and-non-goals.md)
- [ADR Index](docs/coding-agents/adrs/README.md)
- [Implementation Roadmap](docs/coding-agents/implementation-roadmap.md)
