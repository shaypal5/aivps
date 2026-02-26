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
        """Acquire the PID lock using an atomic create operation."""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        current_pid = os.getpid()

        for _ in range(8):
            try:
                fd = os.open(
                    self.pid_file,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o644,
                )
            except FileExistsError:
                existing_pid = _read_pid(self.pid_file)
                if existing_pid is None:
                    self.pid_file.unlink(missing_ok=True)
                    continue

                if pid_is_running(existing_pid):
                    raise PidLockError(
                        f"Daemon appears to be running with pid={existing_pid}"
                    )

                # stale lock: remove and retry atomically
                self.pid_file.unlink(missing_ok=True)
                continue

            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(str(current_pid))
            self.held = True
            return

        raise PidLockError("unable to acquire daemon lock due to concurrent updates")

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
        "stop_requested",
        "not_running",
        "restart_complete",
    ]
    message: str
    pid: int | None = None


class DaemonRunner:
    """Foreground daemon runner that holds the PID lock for its lifetime."""

    def __init__(self, pid_file: Path) -> None:
        self.pid_file = pid_file

    def start(
        self,
        heartbeat_seconds: float = 30.0,
        max_heartbeats: int | None = None,
    ) -> DaemonActionResult:
        """Run daemon heartbeat loop in foreground.

        `max_heartbeats` is the maximum number of sleep cycles to execute.
        """
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

        running = True

        def _handle_signal(_signum: int, _frame: object) -> None:
            nonlocal running
            running = False

        old_sigint = signal.signal(signal.SIGINT, _handle_signal)
        has_sigterm = hasattr(signal, "SIGTERM")
        old_sigterm = None
        if has_sigterm:
            old_sigterm = signal.signal(signal.SIGTERM, _handle_signal)

        try:
            beats = 0
            while running:
                if max_heartbeats is not None and beats >= max_heartbeats:
                    break
                time.sleep(max(heartbeat_seconds, 0.01))
                beats += 1
        finally:
            if old_sigterm is not None:
                signal.signal(signal.SIGTERM, old_sigterm)
            signal.signal(signal.SIGINT, old_sigint)
            lock.release()

        return DaemonActionResult(
            status="started",
            message="daemon run completed",
            pid=os.getpid(),
        )

    def stop(
        self,
        timeout_seconds: float = 5.0,
        poll_interval_seconds: float = 0.1,
    ) -> DaemonActionResult:
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

        term_signal = getattr(signal, "SIGTERM", None)
        if term_signal is None:
            return DaemonActionResult(
                status="stop_requested",
                message="SIGTERM is unavailable on this platform",
                pid=pid,
            )

        try:
            os.kill(pid, term_signal)
        except ProcessLookupError:
            self.pid_file.unlink(missing_ok=True)
            return DaemonActionResult(
                status="stopped",
                message="process already terminated; removed stale pid lock",
                pid=pid,
            )
        except OSError as exc:
            return DaemonActionResult(
                status="stop_requested",
                message=f"failed to send stop signal: {exc}",
                pid=pid,
            )

        deadline = time.monotonic() + max(timeout_seconds, 0.0)
        while time.monotonic() < deadline and pid_is_running(pid):
            time.sleep(max(poll_interval_seconds, 0.01))

        if not pid_is_running(pid):
            self.pid_file.unlink(missing_ok=True)
            return DaemonActionResult(
                status="stopped",
                message="daemon process terminated after SIGTERM",
                pid=pid,
            )

        return DaemonActionResult(
            status="stop_requested",
            message=(
                "sent SIGTERM to daemon process; process still appears to be running"
            ),
            pid=pid,
        )

    def restart(
        self,
        heartbeat_seconds: float = 30.0,
        max_heartbeats: int | None = None,
    ) -> DaemonActionResult:
        stop_result = self.stop()
        if stop_result.status == "stop_requested":
            return DaemonActionResult(
                status="already_running",
                message="restart aborted: existing daemon still running after stop request",
                pid=stop_result.pid,
            )

        start_result = self.start(
            heartbeat_seconds=heartbeat_seconds,
            max_heartbeats=max_heartbeats,
        )
        if start_result.status != "started":
            return start_result

        return DaemonActionResult(
            status="restart_complete",
            message="daemon restart sequence completed",
            pid=start_result.pid,
        )
