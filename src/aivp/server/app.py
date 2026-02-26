"""Server application scaffolding."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ServerConfig:
    root_dir: Path
    db_path: Path
    artifacts_dir: Path
    backups_dir: Path


def build_server_summary(config: ServerConfig) -> dict[str, object]:
    """Return a minimal health summary for local scaffolding checks."""
    summary = asdict(config)
    summary["paths_exist"] = {
        "root_dir": config.root_dir.exists(),
        "db_parent": config.db_path.parent.exists(),
        "artifacts_dir": config.artifacts_dir.exists(),
        "backups_dir": config.backups_dir.exists(),
    }
    return summary
