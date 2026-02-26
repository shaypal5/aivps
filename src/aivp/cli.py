"""Command-line interface for aivp."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

