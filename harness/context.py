from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from .store import HarnessError, Store, atomic_json, now


CONTEXT_PATH = ".harness/context.json"
FIELDS = ("state", "next", "why", "files", "risks", "verify")
MAX_FIELD_CHARS = 700
MAX_TOTAL_CHARS = 2200


def _one_line(value: str) -> str:
    return " ".join(value.split())


def _git_snapshot(root: Path) -> dict[str, str] | None:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).stdout.strip()
        raw = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    ignored = {b".harness/context.json", b".harness/events.jsonl"}
    entries = [
        entry
        for entry in raw.split(b"\0")
        if entry and entry[3:] not in ignored
    ]
    digest = hashlib.sha256(b"\0".join(entries)).hexdigest()
    return {"head": head, "worktree": digest}


def _read(root: Path) -> dict[str, Any] | None:
    path = root / CONTEXT_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 0, "error": "unreadable"}
    return value if isinstance(value, dict) else {"schema_version": 0, "error": "malformed"}


def save_handoff(store: Store, values: dict[str, str]) -> dict[str, Any]:
    normalized = {field: _one_line(values.get(field, "")) for field in FIELDS}
    if not normalized["state"] or not normalized["next"]:
        raise HarnessError("context handoff requires nonempty state and next fields")
    for field, value in normalized.items():
        if len(value) > MAX_FIELD_CHARS:
            raise HarnessError(f"context {field} exceeds {MAX_FIELD_CHARS} characters")
    if sum(map(len, normalized.values())) > MAX_TOTAL_CHARS:
        raise HarnessError(f"context handoff exceeds {MAX_TOTAL_CHARS} characters")
    lock = store.read_lock()
    record = store.rounds.get(lock.get("round_id"), lock) if lock else None
    handoff: dict[str, Any] = {
        "schema_version": 1,
        "saved_at": now(),
        **normalized,
        "register_digest": store.digest(),
        "round_id": record.get("round_id") if record else None,
        "items": list(record.get("items", [])) if record else [],
    }
    handoff["git"] = _git_snapshot(store.root)
    atomic_json(store.root / CONTEXT_PATH, handoff)
    store.append_event(
        "context_saved",
        round_id=handoff["round_id"],
        register_digest=handoff["register_digest"],
    )
    return handoff


def handoff_status(store: Store, handoff: dict[str, Any] | None = None) -> tuple[str, list[str]]:
    handoff = _read(store.root) if handoff is None else handoff
    if handoff is None or handoff.get("schema_version") == 0:
        return "EMPTY", ["manual handoff missing or unreadable"]
    if handoff.get("schema_version") != 1 or not handoff.get("state") or not handoff.get("next"):
        return "EMPTY", ["manual handoff has no established state and next action"]
    reasons: list[str] = []
    if handoff.get("register_digest") != store.digest():
        reasons.append("register changed")
    lock = store.read_lock()
    round_id = lock.get("round_id") if lock else None
    if handoff.get("round_id") != round_id:
        reasons.append("active round changed")
    saved_git = handoff.get("git")
    current_git = _git_snapshot(store.root)
    if saved_git and not current_git:
        reasons.append("git state unavailable")
    elif current_git and not saved_git:
        reasons.append("git boundary added")
    elif saved_git and current_git:
        if saved_git.get("head") != current_git.get("head"):
            reasons.append("git revision changed")
        if saved_git.get("worktree") != current_git.get("worktree"):
            reasons.append("worktree changed")
    return ("STALE", reasons) if reasons else ("FRESH", [])


def render_handoff(store: Store) -> str:
    handoff = _read(store.root)
    status, reasons = handoff_status(store, handoff)
    if not handoff or status == "EMPTY":
        return "HANDOFF EMPTY\nACTION save before deliberate compaction: ./h context save --state \"facts/decisions\" --next \"one exact action\""
    lines = [f"HANDOFF {status} {handoff.get('saved_at', 'unknown time')}"]
    for field in FIELDS:
        lines.append(f"{field.upper()} {handoff.get(field) or 'none'}")
    lines.append(f"ROUND {handoff.get('round_id') or 'none'}")
    lines.append(f"ITEMS {' '.join(handoff.get('items', [])) or 'none'}")
    lines.append(f"REGISTER {str(handoff.get('register_digest', 'unknown'))[:16]}")
    if reasons:
        lines.append("STALE " + "; ".join(reasons))
        lines.append("ACTION run ./h; rewrite handoff before deliberate compaction")
    return "\n".join(lines)
