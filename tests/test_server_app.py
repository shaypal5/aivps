from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aivp.server.app import ServerConfig, build_server_summary


class BuildServerSummaryTests(unittest.TestCase):
    def test_summary_is_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = ServerConfig(
                root_dir=root,
                db_path=root / "runtime" / "db" / "aivp.sqlite3",
                artifacts_dir=root / "runtime" / "artifacts",
                backups_dir=root / "runtime" / "backups",
            )
            summary = build_server_summary(config)

            encoded = json.dumps(summary)
            self.assertIsInstance(encoded, str)
            self.assertEqual(summary["root_dir"], str(root))
            self.assertEqual(
                summary["db_path"], str(root / "runtime" / "db" / "aivp.sqlite3")
            )


if __name__ == "__main__":
    unittest.main()

