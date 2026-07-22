from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .store import Store, atomic_text


def formal_claims(root: Path) -> list[dict[str, object]]:
    try:
        value = json.loads((root / "formal/CLAIMS.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []
    claims = value.get("claims", []) if isinstance(value, dict) else []
    return [claim for claim in claims if isinstance(claim, dict)] if isinstance(claims, list) else []


def formal_claim_lines(root: Path) -> list[str]:
    claims = formal_claims(root)
    lines = ["", "## Formal claims", ""]
    if not claims:
        lines.append("No public formal claim is registered.")
    else:
        for claim in claims:
            lines.append(
                f"- `{claim.get('claim_id', 'invalid')}` — "
                f"`{claim.get('status', 'invalid')}` — "
                f"`{claim.get('declaration', 'missing declaration')}`"
            )
    return lines


def _progress(store: Store) -> tuple[int, int, int]:
    counted = [item for item in store.items.values() if item["status"] != "dropped"]
    done = sum(item["status"] == "done" for item in counted)
    return done, len(counted), round(100 * done / len(counted)) if counted else 0


def recovery_brief(store: Store) -> str:
    done, total, percent = _progress(store)
    project = store.register.get("project", {})
    lock = store.read_lock()
    lines = [
        f"PROJECT  {project.get('title', 'Untitled project')}",
        f"STATE    {project.get('status', 'bootstrap')} · {done}/{total} items ({percent}%)",
    ]
    if lock:
        round_id = lock.get("round_id")
        record = store.rounds.get(round_id, lock)
        lines.append(
            f"ROUND    {round_id} · {record.get('mode')} · {record.get('status', lock.get('phase'))}"
        )
        lines.append(f"ITEMS    {' '.join(record.get('items', [])) or 'none'}")
        note = record.get("last_note")
        if note:
            lines.append(f"LAST     {note.get('text', '')}")
            if note.get("next"):
                lines.append(f"NEXT     {note['next']}")
        else:
            lines.append("NEXT     Add a checkpoint with ./h note '...' --next '...'")
        lines.append(f"RESUME   {record.get('workdir', 'work/')}")
    else:
        ready = store.ready()
        if ready:
            first = ready[0]
            lines.append(f"READY    {first} · {store.items[first]['title']}")
        else:
            lines.append("READY    none")
    blocked = [ident for ident, item in store.items.items() if item["status"] == "blocked"]
    if blocked:
        lines.append(f"BLOCKED  {' '.join(blocked)}")
    return "\n".join(lines)


def full_report(store: Store) -> str:
    done, total, percent = _progress(store)
    project = store.register.get("project", {})
    lines = [
        f"# Project status — {project.get('title', 'Untitled project')}",
        "",
        f"- Project state: `{project.get('status', 'bootstrap')}`",
        f"- Progress: **{done}/{total} ({percent}%)**",
        f"- Register digest: `{store.digest()[:16]}`",
        "",
        "## Lifecycle",
        "",
        "| Stage | Pending | Active | Blocked | Done | Dropped |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for stage in store.stages:
        counts = Counter(
            item["status"] for item in store.items.values() if item["stage"] == stage
        )
        lines.append(
            f"| {stage} | {counts['pending']} | {counts['active']} | {counts['blocked']} | "
            f"{counts['done']} | {counts['dropped']} |"
        )
    lines.extend(["", "## Current round", ""])
    lock = store.read_lock()
    if lock:
        record = store.rounds.get(lock.get("round_id"), lock)
        lines.extend(
            [
                f"- `{record.get('round_id')}` in **{record.get('mode')}** mode",
                f"- Items: {', '.join(f'`{item}`' for item in record.get('items', [])) or 'none'}",
                f"- Work directory: `{record.get('workdir')}`",
            ]
        )
        if record.get("last_note"):
            lines.append(f"- Last checkpoint: {record['last_note'].get('text', '')}")
            if record["last_note"].get("next"):
                lines.append(f"- Resume action: {record['last_note']['next']}")
    else:
        lines.append("No round is open.")
    lines.extend(["", "## Blockers", ""])
    blockers = [(ident, item) for ident, item in store.items.items() if item["status"] == "blocked"]
    if blockers:
        for ident, item in blockers:
            lines.append(f"- `{ident}` — {item['title']}: {item.get('blocked_reason', 'reason not recorded')}")
    else:
        lines.append("None.")
    lines.extend(["", "## Ready next", ""])
    ready = store.ready()
    if ready:
        for ident in ready[:10]:
            item = store.items[ident]
            lines.append(f"- `{ident}` [{item['mode']}] — {item['title']} (`{item['stage']}`)")
    else:
        lines.append("No dependency-ready items.")
    lines.extend(formal_claim_lines(store.root))
    lines.extend(["", "## Recent events", ""])
    events = store.event_tail(6)
    if events:
        for event in reversed(events):
            lines.append(f"- {event.get('at')} — `{event.get('kind')}`")
    else:
        lines.append("No events yet.")
    return "\n".join(lines) + "\n"


def next_report(store: Store) -> str:
    lines = ["# Next", "", "This file is generated by `./h report --write`.", ""]
    lock = store.read_lock()
    if lock:
        record = store.rounds.get(lock.get("round_id"), lock)
        lines.extend(
            [
                f"## Resume `{record.get('round_id')}`",
                "",
                f"- Mode: `{record.get('mode')}`",
                f"- Items: {', '.join(f'`{item}`' for item in record.get('items', [])) or 'none'}",
                f"- Work directory: `{record.get('workdir')}`",
            ]
        )
        note = record.get("last_note")
        if note and note.get("next"):
            lines.append(f"- Exact next action: {note['next']}")
        else:
            lines.append("- Exact next action: record one with `./h note ... --next ...`.")
    else:
        lines.extend(["## Start a round", ""])
        for ident in store.ready()[:10]:
            item = store.items[ident]
            lines.append(
                f"- `{ident}` [{item['mode']}] — {item['title']} · tags: {', '.join(item['tags']) or 'none'}"
            )
        if not store.ready():
            lines.append("No items are ready. Inspect blockers and dependencies with `./h report`.")
    return "\n".join(lines) + "\n"


def write_reports(store: Store) -> tuple[Path, Path]:
    status = store.root / "STATUS.md"
    next_path = store.root / "NEXT.md"
    atomic_text(status, full_report(store))
    atomic_text(next_path, next_report(store))
    return status, next_path
