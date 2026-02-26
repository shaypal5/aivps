"""Command-line interface for aivp."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from aivp.runtime.db import bootstrap_sqlite
from aivp.runtime.daemon import DaemonRunner
from aivp.server.app import ServerConfig, build_server_summary


def _cmd_doctor(args: argparse.Namespace) -> int:
    config = ServerConfig(
        root_dir=Path(args.root).resolve(),
        db_path=Path(args.db_path).resolve(),
        artifacts_dir=Path(args.artifacts_dir).resolve(),
        backups_dir=Path(args.backups_dir).resolve(),
    )
    print(json.dumps(build_server_summary(config), indent=2))
    return 0


def _cmd_daemon_start(args: argparse.Namespace) -> int:
    result = DaemonRunner(Path(args.pid_file).resolve()).start(
        heartbeat_seconds=args.heartbeat_seconds,
        max_heartbeats=args.max_heartbeats,
    )
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.status in {"started", "restart_complete"} else 1


def _cmd_daemon_stop(args: argparse.Namespace) -> int:
    result = DaemonRunner(Path(args.pid_file).resolve()).stop()
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.status in {"stopped", "not_running"} else 1


def _cmd_daemon_restart(args: argparse.Namespace) -> int:
    result = DaemonRunner(Path(args.pid_file).resolve()).restart(
        heartbeat_seconds=args.heartbeat_seconds,
        max_heartbeats=args.max_heartbeats,
    )
    print(json.dumps(asdict(result), indent=2))
    return 0


def _cmd_db_init(args: argparse.Namespace) -> int:
    result = bootstrap_sqlite(
        db_path=Path(args.db_path).resolve(),
        initial_migration_version=args.migration_version,
    )
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.wal_enabled else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aivp",
        description="Local-first mini-agent framework for focused AI VPs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor",
        help="Print a scaffold sanity summary.",
    )
    doctor.add_argument("--root", default=".")
    doctor.add_argument("--db-path", default="runtime/db/aivp.sqlite3")
    doctor.add_argument("--artifacts-dir", default="runtime/artifacts")
    doctor.add_argument("--backups-dir", default="runtime/backups")
    doctor.set_defaults(func=_cmd_doctor)

    daemon = subparsers.add_parser("daemon", help="Daemon lifecycle controls.")
    daemon_subparsers = daemon.add_subparsers(dest="daemon_command", required=True)

    daemon_start = daemon_subparsers.add_parser(
        "start", help="Start foreground daemon."
    )
    daemon_start.add_argument("--pid-file", default="runtime/daemon.pid")
    daemon_start.add_argument("--heartbeat-seconds", type=float, default=30.0)
    daemon_start.add_argument(
        "--max-heartbeats",
        type=int,
        help="Maximum number of heartbeat sleep cycles before exiting.",
    )
    daemon_start.set_defaults(func=_cmd_daemon_start)

    daemon_stop = daemon_subparsers.add_parser("stop", help="Stop daemon by pid file.")
    daemon_stop.add_argument("--pid-file", default="runtime/daemon.pid")
    daemon_stop.set_defaults(func=_cmd_daemon_stop)

    daemon_restart = daemon_subparsers.add_parser(
        "restart", help="Restart daemon using pid file."
    )
    daemon_restart.add_argument("--pid-file", default="runtime/daemon.pid")
    daemon_restart.add_argument("--heartbeat-seconds", type=float, default=30.0)
    daemon_restart.add_argument(
        "--max-heartbeats",
        type=int,
        help="Maximum number of heartbeat sleep cycles before exiting.",
    )
    daemon_restart.set_defaults(func=_cmd_daemon_restart)

    db = subparsers.add_parser("db", help="Runtime database operations.")
    db_subparsers = db.add_subparsers(dest="db_command", required=True)

    db_init = db_subparsers.add_parser(
        "init",
        help="Initialize runtime SQLite DB with WAL mode and schema state table.",
    )
    db_init.add_argument("--db-path", default="runtime/db/aivp.sqlite3")
    db_init.add_argument("--migration-version", default="v1alpha1")
    db_init.set_defaults(func=_cmd_db_init)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
