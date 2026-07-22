from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid


MAX_SECONDS = 240
DEFAULT_SECONDS = 240
DEFAULT_NICE = 10
MIN_NICE = 5
TERM_GRACE_SECONDS = 3
SINGLE_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
}


class RuntimeControlError(RuntimeError):
    pass


class RuntimeBusy(RuntimeControlError):
    pass


@dataclass(frozen=True)
class RuntimePaths:
    lock: Path
    directory: Path
    last_run: Path
    events: Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def paths(root: Path) -> RuntimePaths:
    state = root / ".harness"
    directory = state / "runtime"
    return RuntimePaths(
        lock=state / "compute.lock",
        directory=directory,
        last_run=directory / "last-run.json",
        events=directory / "events.jsonl",
    )


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _append_event(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _read_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def _pid_alive(value: object) -> bool:
    if not isinstance(value, int) or value <= 0:
        return False
    try:
        os.kill(value, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lock_state(root: Path) -> tuple[str, dict[str, object] | None]:
    record = _read_json(paths(root).lock)
    if record is None:
        return "none", None
    if _pid_alive(record.get("parent_pid")) or _pid_alive(record.get("child_pid")):
        return "active", record
    return "stale", record


def _acquire_lock(root: Path, record: dict[str, object]) -> None:
    runtime_paths = paths(root)
    runtime_paths.lock.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(2):
        try:
            descriptor = os.open(
                runtime_paths.lock,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            state, previous = lock_state(root)
            if state == "active":
                label = previous.get("label", "unlabelled") if previous else "unlabelled"
                started = previous.get("started_at", "unknown") if previous else "unknown"
                raise RuntimeBusy(
                    f"compute lock is active: label={label!r} started={started}; "
                    "run ./h run-status and do not start a replacement"
                )
            if state == "stale" and attempt == 0:
                runtime_paths.lock.unlink(missing_ok=True)
                print("RUN recovered stale compute lock; previous processes are no longer alive")
                continue
            raise RuntimeControlError("compute lock exists but cannot be read safely")
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            return
    raise RuntimeControlError("could not acquire compute lock")


def _release_lock(root: Path, token: str) -> None:
    runtime_paths = paths(root)
    current = _read_json(runtime_paths.lock)
    if current and current.get("token") == token:
        runtime_paths.lock.unlink(missing_ok=True)


def _command_name(command: str) -> str:
    try:
        words = shlex.split(command)
    except ValueError:
        words = command.split()
    return Path(words[0]).name if words else "unknown"


def process_audit(limit: int = 8) -> list[dict[str, object]]:
    ps = shutil.which("ps")
    if not ps:
        return [{"error": "ps unavailable"}]
    try:
        completed = subprocess.run(
            [ps, "-axo", "pid=,ppid=,%cpu=,%mem=,etime=,command="],
            text=True,
            capture_output=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [{"error": str(exc)}]
    rows: list[dict[str, object]] = []
    for line in completed.stdout.splitlines():
        columns = line.strip().split(None, 5)
        if len(columns) < 6:
            continue
        try:
            pid, parent = int(columns[0]), int(columns[1])
            cpu, memory = float(columns[2]), float(columns[3])
        except ValueError:
            continue
        if pid == os.getpid():
            continue
        rows.append(
            {
                "pid": pid,
                "parent_pid": parent,
                "cpu_percent": cpu,
                "memory_percent": memory,
                "elapsed": columns[4],
                "executable": _command_name(columns[5]),
            }
        )
    rows.sort(key=lambda row: (float(row["cpu_percent"]), float(row["memory_percent"])), reverse=True)
    return rows[:limit]


def _terminate_group(process: subprocess.Popen[object]) -> str:
    if process.poll() is not None:
        return "already-exited"
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return "already-exited"
    try:
        process.wait(timeout=TERM_GRACE_SECONDS)
        return "terminated"
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        return "killed"


def _validate(command: list[str], timeout_seconds: float, nice_level: int) -> None:
    if not command:
        raise RuntimeControlError("no command supplied after --")
    if timeout_seconds <= 0 or timeout_seconds > MAX_SECONDS:
        raise RuntimeControlError(f"timeout must be greater than zero and at most {MAX_SECONDS} seconds")
    if nice_level < MIN_NICE or nice_level > 19:
        raise RuntimeControlError(f"nice level must be between {MIN_NICE} and 19")
    forbidden = {"&", "nohup", "disown", "bg"}
    if any(part.casefold() in forbidden for part in command):
        raise RuntimeControlError("backgrounding and daemon launchers are forbidden in guarded runs")


def run_guarded(
    root: Path,
    command: list[str],
    *,
    cwd: Path | None = None,
    label: str = "ad-hoc",
    timeout_seconds: float = DEFAULT_SECONDS,
    nice_level: int = DEFAULT_NICE,
) -> int:
    root = root.resolve()
    working = (cwd or root).resolve()
    _validate(command, timeout_seconds, nice_level)
    try:
        relative_working = working.relative_to(root)
    except ValueError as exc:
        raise RuntimeControlError("guarded working directory must remain inside the project") from exc
    if not working.is_dir():
        raise RuntimeControlError(f"guarded working directory does not exist: {working}")
    nice = shutil.which("nice")
    if not nice:
        raise RuntimeControlError("POSIX nice is required for guarded computation")

    token = uuid.uuid4().hex
    started_at = now()
    try:
        current_nice = os.getpriority(os.PRIO_PROCESS, 0)
    except (AttributeError, OSError):
        current_nice = 0
    nice_increment = max(0, nice_level - current_nice)
    record: dict[str, object] = {
        "schema_version": 1,
        "token": token,
        "status": "starting",
        "label": label,
        "started_at": started_at,
        "parent_pid": os.getpid(),
        "child_pid": None,
        "process_group": None,
        "cwd": str(relative_working) or ".",
        "command": command,
        "timeout_seconds": timeout_seconds,
        "nice_level": nice_level,
        "thread_limits": SINGLE_THREAD_ENV,
    }
    _acquire_lock(root, record)
    runtime_paths = paths(root)
    _atomic_json(runtime_paths.last_run, record)
    _append_event(runtime_paths.events, {"at": started_at, "kind": "run_started", **record})
    process: subprocess.Popen[object] | None = None
    original_handlers: dict[int, object] = {}
    interrupted_signal: int | None = None

    def interrupt(signum: int, _frame: object) -> None:
        nonlocal interrupted_signal
        interrupted_signal = signum
        raise KeyboardInterrupt

    try:
        for candidate in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            original_handlers[candidate] = signal.getsignal(candidate)
            signal.signal(candidate, interrupt)
        launched = [nice, "-n", str(nice_increment), *command]
        print(
            f"RUN label={label!r} timeout={timeout_seconds:g}s nice>={nice_level} "
            f"cwd={record['cwd']}",
            flush=True,
        )
        environment = os.environ.copy()
        environment.update(SINGLE_THREAD_ENV)
        process = subprocess.Popen(
            launched,
            cwd=working,
            env=environment,
            start_new_session=True,
        )
        record.update(
            {
                "status": "running",
                "child_pid": process.pid,
                "process_group": process.pid,
            }
        )
        _atomic_json(runtime_paths.lock, record)
        _atomic_json(runtime_paths.last_run, record)
        began = time.monotonic()
        try:
            return_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - began
            termination = _terminate_group(process)
            audit = process_audit()
            record.update(
                {
                    "status": "timeout",
                    "finished_at": now(),
                    "elapsed_seconds": round(elapsed, 3),
                    "exit_code": 124,
                    "termination": termination,
                    "process_audit": audit,
                }
            )
            _atomic_json(runtime_paths.last_run, record)
            _append_event(runtime_paths.events, {"at": record["finished_at"], "kind": "run_timeout", **record})
            print(
                f"WATCHDOG timeout after {timeout_seconds:g}s; process group {process.pid} {termination}",
                file=sys.stderr,
            )
            print("PROCESS AUDIT (commands reduced to executable names)", file=sys.stderr)
            for row in audit:
                print(f"- {json.dumps(row, sort_keys=True)}", file=sys.stderr)
            print(
                "DO NOT RETRY. If another process is competing, wait or coordinate; otherwise refactor the task.",
                file=sys.stderr,
            )
            return 124
        else:
            elapsed = time.monotonic() - began
            status = "passed" if return_code == 0 else "failed"
            record.update(
                {
                    "status": status,
                    "finished_at": now(),
                    "elapsed_seconds": round(elapsed, 3),
                    "exit_code": return_code,
                }
            )
            _atomic_json(runtime_paths.last_run, record)
            _append_event(runtime_paths.events, {"at": record["finished_at"], "kind": f"run_{status}", **record})
            print(f"RUN {status} elapsed={elapsed:.2f}s exit={return_code}", flush=True)
            return return_code
    except KeyboardInterrupt:
        termination = _terminate_group(process) if process is not None else "not-started"
        code = 128 + (interrupted_signal or signal.SIGINT)
        record.update(
            {
                "status": "interrupted",
                "finished_at": now(),
                "exit_code": code,
                "termination": termination,
                "process_audit": process_audit(),
            }
        )
        _atomic_json(runtime_paths.last_run, record)
        _append_event(runtime_paths.events, {"at": record["finished_at"], "kind": "run_interrupted", **record})
        return code
    except OSError as exc:
        if process is not None:
            _terminate_group(process)
        record.update({"status": "launch-failed", "finished_at": now(), "error": str(exc), "exit_code": 126})
        _atomic_json(runtime_paths.last_run, record)
        _append_event(runtime_paths.events, {"at": record["finished_at"], "kind": "run_launch_failed", **record})
        print(f"RUN launch failed: {exc}", file=sys.stderr)
        return 126
    finally:
        for candidate, handler in original_handlers.items():
            signal.signal(candidate, handler)
        _release_lock(root, token)


def runtime_snapshot(root: Path) -> dict[str, object]:
    state, lock = lock_state(root)
    return {
        "lock_state": state,
        "lock": lock,
        "last_run": _read_json(paths(root).last_run),
    }


def runtime_brief(root: Path) -> str:
    snapshot = runtime_snapshot(root)
    state = snapshot["lock_state"]
    lock = snapshot["lock"]
    if state in {"active", "stale"} and isinstance(lock, dict):
        return (
            f"COMPUTE {state} label={lock.get('label', 'unknown')} "
            f"started={lock.get('started_at', 'unknown')} command={lock.get('command', [])}"
        )
    last = snapshot["last_run"]
    if isinstance(last, dict) and last.get("status") in {"running", "timeout", "interrupted", "launch-failed"}:
        return (
            f"COMPUTE last={last.get('status')} label={last.get('label', 'unknown')} "
            f"finished={last.get('finished_at', 'unknown')} command={last.get('command', [])}"
        )
    return ""
