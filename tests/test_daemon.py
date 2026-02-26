from __future__ import annotations

import os
import signal
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aivp.runtime.daemon import (
    DaemonActionResult,
    DaemonRunner,
    PidFileLock,
    PidLockError,
)


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
                    self.assertEqual(
                        pid_file.read_text(encoding="utf-8"), str(os.getpid())
                    )
                finally:
                    lock.release()


class DaemonRunnerTests(unittest.TestCase):
    def test_start_returns_already_running_when_pid_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")

            result = DaemonRunner(pid_file).start(
                max_heartbeats=1, heartbeat_seconds=0.01
            )
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

            with patch(
                "aivp.runtime.daemon.pid_is_running",
                side_effect=[True, False, False],
            ):
                with patch("aivp.runtime.daemon.os.kill") as kill_mock:
                    result = DaemonRunner(pid_file).stop()

            self.assertEqual(result.status, "stopped")
            kill_mock.assert_called_once_with(1234, signal.SIGTERM)

    def test_stop_handles_process_lookup_race(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            pid_file.write_text("1234", encoding="utf-8")

            with patch("aivp.runtime.daemon.pid_is_running", return_value=True):
                with patch(
                    "aivp.runtime.daemon.os.kill", side_effect=ProcessLookupError
                ):
                    result = DaemonRunner(pid_file).stop()

            self.assertEqual(result.status, "stopped")
            self.assertFalse(pid_file.exists())

    def test_start_runner_can_be_reused(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "daemon.pid"
            runner = DaemonRunner(pid_file)

            first = runner.start(max_heartbeats=0)
            second = runner.start(max_heartbeats=0)

            self.assertEqual(first.status, "started")
            self.assertEqual(second.status, "started")

    def test_restart_passes_parameters_to_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = DaemonRunner(Path(tmpdir) / "daemon.pid")

            with patch.object(
                runner,
                "stop",
                return_value=DaemonActionResult(
                    status="stopped",
                    message="stopped",
                    pid=111,
                ),
            ):
                with patch.object(
                    runner,
                    "start",
                    return_value=DaemonActionResult(
                        status="started",
                        message="started",
                        pid=222,
                    ),
                ) as start_mock:
                    result = runner.restart(
                        heartbeat_seconds=0.25,
                        max_heartbeats=5,
                    )

            self.assertEqual(result.status, "restart_complete")
            start_mock.assert_called_once_with(
                heartbeat_seconds=0.25,
                max_heartbeats=5,
            )

    def test_restart_aborts_when_stop_does_not_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = DaemonRunner(Path(tmpdir) / "daemon.pid")

            with patch.object(
                runner,
                "stop",
                return_value=DaemonActionResult(
                    status="stop_requested",
                    message="still running",
                    pid=333,
                ),
            ):
                with patch.object(runner, "start") as start_mock:
                    result = runner.restart()

            self.assertEqual(result.status, "already_running")
            start_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
