from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aivp.runtime.daemon import DaemonRunner, PidFileLock, PidLockError


class PidFileLockTests(unittest.TestCase):
    def test_second_instance_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            lock1 = PidFileLock(pid_file)
            lock1.acquire()

            lock2 = PidFileLock(pid_file)
            with self.assertRaises(PidLockError):
                lock2.acquire()

            lock1.release()

    def test_stale_lock_is_recovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text("999999", encoding="utf-8")

            with patch("aivp.runtime.daemon.pid_is_running", return_value=False):
                lock = PidFileLock(pid_file)
                lock.acquire()
                try:
                    self.assertEqual(pid_file.read_text(encoding="utf-8"), str(os.getpid()))
                finally:
                    lock.release()


class DaemonRunnerTests(unittest.TestCase):
    def test_start_returns_already_running_when_pid_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")

            result = DaemonRunner(pid_file).start(max_heartbeats=1, heartbeat_seconds=0.01)
            self.assertEqual(result.status, "already_running")

    def test_stop_removes_stale_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text("999999", encoding="utf-8")

            with patch("aivp.runtime.daemon.pid_is_running", return_value=False):
                result = DaemonRunner(pid_file).stop()

            self.assertEqual(result.status, "stopped")
            self.assertFalse(pid_file.exists())

    def test_stop_sends_sigterm_for_running_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text("1234", encoding="utf-8")

            with patch("aivp.runtime.daemon.pid_is_running", return_value=True):
                with patch("aivp.runtime.daemon.os.kill") as kill_mock:
                    result = DaemonRunner(pid_file).stop()

            self.assertEqual(result.status, "stopped")
            kill_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()

