"""Daemon lifecycle and PID lock utilities."""

from __future__ import annotations

import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


class PidLockError(RuntimeError):
    """Raised when a daemon lock cannot be acquired."""


def pid_is_running(pid: int) -> bool:
    """Return True when the process exists or is inaccessible by permissions."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_pid(pid_file: Path) -> int | None:
    if not pid_file.exists():
        return None
    raw = pid_file.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


@dataclass
class PidFileLock:
    """Exclusive lock represented by a PID file."""

    pid_file: Path
    held: bool = False

    def acquire(self) -> None:
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        existing_pid = _read_pid(self.pid_file)

        if existing_pid is not None:
            if pid_is_running(existing_pid):
                raise PidLockError(
                    f"Daemon appears to be running with pid={existing_pid}"
                )
            # stale lock: remove and continue
            self.pid_file.unlink(missing_ok=True)

        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")
        self.held = True

    def release(self) -> None:
        if not self.held:
            return
        current_pid = _read_pid(self.pid_file)
        if current_pid == os.getpid():
            self.pid_file.unlink(missing_ok=True)
        self.held = False


@dataclass(frozen=True)
class DaemonActionResult:
    status: Literal[
        "started",
        "already_running",
        "stopped",
        "not_running",
        "restart_complete",
    ]
    message: str
    pid: int | None = None


class DaemonRunner:
    """Foreground daemon runner that holds the PID lock for its lifetime."""

    def __init__(self, pid_file: Path) -> None:
        self.pid_file = pid_file
        self._running = True

    def _handle_signal(self, _signum: int, _frame: object) -> None:
        self._running = False

    def start(
        self,
        heartbeat_seconds: float = 30.0,
        max_heartbeats: int | None = None,
    ) -> DaemonActionResult:
        lock = PidFileLock(self.pid_file)
        try:
            lock.acquire()
        except PidLockError:
            existing_pid = _read_pid(self.pid_file)
            return DaemonActionResult(
                status="already_running",
                message="daemon start blocked by active pid lock",
                pid=existing_pid,
            )

        old_sigterm = signal.signal(signal.SIGTERM, self._handle_signal)
        old_sigint = signal.signal(signal.SIGINT, self._handle_signal)
        try:
            beats = 0
            while self._running:
                if max_heartbeats is not None and beats >= max_heartbeats:
                    break
                time.sleep(max(heartbeat_seconds, 0.01))
                beats += 1
        finally:
            signal.signal(signal.SIGTERM, old_sigterm)
            signal.signal(signal.SIGINT, old_sigint)
            lock.release()

        return DaemonActionResult(
            status="started",
            message="daemon run completed",
            pid=os.getpid(),
        )

    def stop(self) -> DaemonActionResult:
        pid = _read_pid(self.pid_file)
        if pid is None:
            return DaemonActionResult(
                status="not_running",
                message="no pid lock present",
            )

        if not pid_is_running(pid):
            self.pid_file.unlink(missing_ok=True)
            return DaemonActionResult(
                status="stopped",
                message="removed stale pid lock",
                pid=pid,
            )

        os.kill(pid, signal.SIGTERM)
        return DaemonActionResult(
            status="stopped",
            message="sent SIGTERM to daemon process",
            pid=pid,
        )

    def restart(
        self,
        heartbeat_seconds: float = 30.0,
        max_heartbeats: int | None = None,
    ) -> DaemonActionResult:
        self.stop()
        start_result = self.start(
            heartbeat_seconds=heartbeat_seconds,
            max_heartbeats=max_heartbeats,
        )
        return DaemonActionResult(
            status="restart_complete",
            message="daemon restart sequence completed",
            pid=start_result.pid,
        )
