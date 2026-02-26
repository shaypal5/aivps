from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from aivp.runtime.db import (
    bootstrap_sqlite,
    get_migration_version,
    set_migration_version,
)


class RuntimeDbBootstrapTests(unittest.TestCase):
    def test_bootstrap_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3"

            first = bootstrap_sqlite(db_path, initial_migration_version="v1alpha1")
            second = bootstrap_sqlite(db_path, initial_migration_version="v9ignored")

            self.assertTrue(first.wal_enabled)
            self.assertEqual(first.journal_mode, "wal")
            self.assertTrue(first.created_state_row)

            self.assertFalse(second.created_state_row)
            self.assertEqual(second.migration_version, "v1alpha1")
            self.assertEqual(get_migration_version(db_path), "v1alpha1")

    def test_migration_version_persists_across_restarts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3"

            bootstrap_sqlite(db_path, initial_migration_version="v1alpha1")
            set_migration_version(db_path, "v1alpha2")

            self.assertEqual(get_migration_version(db_path), "v1alpha2")

            # Simulate restart by reinitializing and rereading state.
            bootstrap_sqlite(db_path, initial_migration_version="v0")
            self.assertEqual(get_migration_version(db_path), "v1alpha2")

    def test_get_migration_version_returns_none_when_db_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "missing.sqlite3"
            self.assertFalse(db_path.exists())

            version = get_migration_version(db_path)

            self.assertIsNone(version)
            self.assertFalse(db_path.exists())

    def test_get_migration_version_returns_none_when_table_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "existing.sqlite3"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY)")
                conn.commit()

            version = get_migration_version(db_path)
            self.assertIsNone(version)


if __name__ == "__main__":
    unittest.main()
