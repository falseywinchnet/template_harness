from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .parser import ParsedItem


ITEM_ID = re.compile(r"^P\d{3,6}$")
ROUND_ID = re.compile(r"^R\d{4,6}$")
STATUSES = {"pending", "active", "blocked", "done", "dropped"}
MODES = {"advance", "refine", "either"}


class HarnessError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    return value[:48] or "round"


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.state_dir = self.root / ".harness"
        self.register_path = self.state_dir / "register.json"
        self.config_path = self.state_dir / "config.json"
        self.events_path = self.state_dir / "events.jsonl"
        self.lock_path = self.state_dir / "round.lock"
        self.register = self._load(self.register_path)
        self.config = self._load(self.config_path)

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise HarnessError(f"missing harness file: {path}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise HarnessError(f"cannot load {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise HarnessError(f"expected JSON object in {path}")
        return value

    @property
    def items(self) -> dict[str, dict[str, Any]]:
        return self.register["items"]

    @property
    def rounds(self) -> dict[str, dict[str, Any]]:
        return self.register["rounds"]

    @property
    def stages(self) -> list[str]:
        return list(self.config["stages"])

    def save(self) -> None:
        errors = self.validate(include_lock=False)
        if errors:
            raise HarnessError("register validation failed:\n  " + "\n  ".join(errors))
        atomic_json(self.register_path, self.register)

    def append_event(self, kind: str, **fields: Any) -> None:
        event = {"at": now(), "kind": kind, **fields}
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
        descriptor = os.open(self.events_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(descriptor, data)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def allocate_item(self) -> str:
        number = int(self.register["next_item"])
        while f"P{number:03d}" in self.items:
            number += 1
        self.register["next_item"] = number + 1
        return f"P{number:03d}"

    def register_items(self, parsed: list[ParsedItem], source: str) -> tuple[list[str], list[str]]:
        created: list[str] = []
        updated: list[str] = []
        seen: set[str] = set()
        for candidate in parsed:
            ident = candidate.ident or self.allocate_item()
            if ident in seen:
                raise HarnessError(f"duplicate item {ident} in input")
            seen.add(ident)
            if candidate.stage not in self.stages:
                raise HarnessError(
                    f"{ident}: unknown stage {candidate.stage!r}; choose from {', '.join(self.stages)}"
                )
            stamp = now()
            fields = {
                "id": ident,
                "title": candidate.title,
                "stage": candidate.stage,
                "mode": candidate.mode,
                "tags": list(candidate.tags),
                "depends": list(candidate.depends),
                "acceptance": candidate.acceptance,
                "source": source,
                "source_line": candidate.line,
                "updated_at": stamp,
            }
            if ident in self.items:
                previous = self.items[ident]
                runtime = {
                    key: previous.get(key)
                    for key in ("status", "blocked_reason", "completed_at", "active_round")
                    if key in previous
                }
                previous.update(fields)
                previous.update(runtime)
                updated.append(ident)
            else:
                if candidate.status in {"blocked", "dropped"} and not candidate.reason:
                    raise HarnessError(
                        f"{ident}: a new {candidate.status} item requires reason=..."
                    )
                created_item = {
                    **fields,
                    "status": candidate.status,
                    "created_at": stamp,
                    "active_round": None,
                }
                if candidate.status == "blocked":
                    created_item["blocked_reason"] = candidate.reason
                if candidate.status == "dropped":
                    created_item["dropped_reason"] = candidate.reason
                self.items[ident] = created_item
                created.append(ident)
        self.save()
        self.append_event("register", source=source, created=created, updated=updated)
        return created, updated

    def ready(self, mode: str | None = None, tags: set[str] | None = None) -> list[str]:
        order = {name: index for index, name in enumerate(self.stages)}
        candidates: list[str] = []
        for ident, item in self.items.items():
            if item["status"] != "pending":
                continue
            if mode and item["mode"] not in {mode, "either"}:
                continue
            if tags and not (set(item["tags"]) & tags or ident.casefold() in tags):
                continue
            if any(
                self.items.get(dep, {}).get("status") not in {"done", "dropped"}
                for dep in item["depends"]
            ):
                continue
            candidates.append(ident)
        candidates.sort(key=lambda ident: (order.get(self.items[ident]["stage"], 999), ident))
        if not tags and candidates:
            first_stage = self.items[candidates[0]]["stage"]
            candidates = [ident for ident in candidates if self.items[ident]["stage"] == first_stage]
        return candidates

    def read_lock(self) -> dict[str, Any] | None:
        if not self.lock_path.exists():
            return None
        try:
            value = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HarnessError(f"round lock is unreadable: {exc}") from exc
        if not isinstance(value, dict):
            raise HarnessError("round lock is malformed")
        return value

    def acquire_lock(self, payload: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        try:
            descriptor = os.open(self.lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError as exc:
            lock = self.read_lock() or {}
            raise HarnessError(
                f"{lock.get('round_id', 'a round')} is already open in {lock.get('mode', 'unknown')} "
                "mode; run './h recover' instead of starting another round"
            ) from exc
        try:
            os.write(descriptor, data)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def replace_lock(self, payload: dict[str, Any]) -> None:
        atomic_json(self.lock_path, payload)

    def release_lock(self) -> None:
        try:
            self.lock_path.unlink()
        except FileNotFoundError:
            pass

    def _round_files(self, record: dict[str, Any]) -> None:
        directory = self.root / record["workdir"]
        directory.mkdir(parents=True, exist_ok=True)
        item_lines = [
            f"- `{ident}` — {self.items[ident]['title']}" for ident in record.get("items", [])
        ] or ["- No item was selected."]
        round_text = (
            f"# {record['round_id']} — {record['mode']}\n\n"
            f"- Status: {record['status']}\n"
            f"- Started: {record['started_at']}\n"
            f"- Tags: {', '.join(record.get('tags', [])) or 'none'}\n"
            f"- Resume count: {record.get('resume_count', 0)}\n\n"
            "## Active project items\n\n"
            + "\n".join(item_lines)
            + "\n\n## Round contract\n\n"
            "Work only in the declared mode. Preserve attempts, failures, evidence, and the next exact action.\n"
        )
        atomic_text(directory / "ROUND.md", round_text)
        for name, heading, prompt in (
            ("NOTES.md", "Notes", "Append short, timestamped checkpoints with `./h note`."),
            ("NEXT.md", "Next", "Name the smallest exact action that resumes this round."),
            ("RESULTS.md", "Results", "Record supported results and their evidence boundary."),
            ("FAILURES.md", "Failures", "Record failed routes, counterexamples, and why they failed."),
        ):
            path = directory / name
            if not path.exists():
                atomic_text(path, f"# {heading}\n\n{prompt}\n")

    def start_round(self, mode: str, raw_tags: list[str]) -> dict[str, Any]:
        tags = {
            token.strip().removeprefix("#").casefold()
            for group in raw_tags
            for token in group.split(",")
            if token.strip()
        }
        selected = self.ready(mode=mode, tags=tags or None)
        if not selected:
            raise HarnessError(
                f"no ready {mode} items match {', '.join(sorted(tags)) or 'the earliest stage'}; "
                "run './h report' to inspect dependencies and modes"
            )
        number = int(self.register["next_round"])
        round_id = f"R{number:04d}"
        self.register["next_round"] = number + 1
        label = "-".join(sorted(tags)) if tags else self.items[selected[0]]["stage"]
        workdir = f"work/{round_id}-{mode}-{slug(label)}"
        record = {
            "round_id": round_id,
            "mode": mode,
            "tags": sorted(tags),
            "items": selected,
            "status": "open",
            "started_at": now(),
            "workdir": workdir,
            "resume_count": 0,
        }
        lock = {
            **record,
            "schema_version": 1,
            "host": socket.gethostname(),
            "created_by_pid": os.getpid(),
            "phase": "provisional",
        }
        self.acquire_lock(lock)
        try:
            self.rounds[round_id] = record
            self.register["active_round"] = round_id
            for ident in selected:
                self.items[ident]["status"] = "active"
                self.items[ident]["active_round"] = round_id
                self.items[ident]["updated_at"] = now()
            self.save()
            self._round_files(record)
            lock["phase"] = "active"
            self.replace_lock(lock)
            self.append_event("round_started", round_id=round_id, mode=mode, items=selected, tags=sorted(tags))
        except Exception:
            # The provisional lock is intentionally retained: recover can show
            # exactly what was being activated if a later write failed.
            raise
        return record

    def active_round(self) -> tuple[dict[str, Any], dict[str, Any]]:
        lock = self.read_lock()
        if not lock:
            raise HarnessError("no round is open")
        round_id = lock.get("round_id")
        record = self.rounds.get(round_id)
        if not record:
            raise HarnessError(
                f"lock names {round_id}, but the register does not; run './h resume' to repair it"
            )
        return lock, record

    def resume_round(self) -> dict[str, Any]:
        lock = self.read_lock()
        if not lock:
            raise HarnessError("no interrupted or open round exists")
        round_id = lock.get("round_id")
        if not ROUND_ID.fullmatch(str(round_id)):
            raise HarnessError("round lock has no valid round ID")
        record = self.rounds.get(round_id)
        if record is None:
            record = {
                key: lock[key]
                for key in ("round_id", "mode", "tags", "items", "status", "started_at", "workdir")
                if key in lock
            }
            record.setdefault("status", "open")
            record.setdefault("resume_count", 0)
            self.rounds[round_id] = record
        if record.get("status") == "closed":
            self.register["active_round"] = None
            self.save()
            self._round_files(record)
            results_path = self.root / record["workdir"] / "RESULTS.md"
            marker = f"## Close — {record.get('closed_at')}"
            current = results_path.read_text(encoding="utf-8")
            if marker not in current:
                with results_path.open("a", encoding="utf-8") as stream:
                    stream.write(
                        f"\n{marker}\n\n{record.get('summary') or 'No result summary supplied.'}\n"
                    )
                    stream.flush()
                    os.fsync(stream.fileno())
            self.append_event("closed_lock_recovered", round_id=round_id)
            self.release_lock()
            record["recovery_action"] = "finalized_close"
            return record
        if record.get("status") != "open":
            raise HarnessError(f"{round_id} has unsupported status {record.get('status')!r}")
        record["resume_count"] = int(record.get("resume_count", 0)) + 1
        record["resumed_at"] = now()
        self.register["active_round"] = round_id
        for ident in record.get("items", []):
            if ident not in self.items:
                raise HarnessError(f"{round_id} refers to missing item {ident}")
            if self.items[ident]["status"] not in {"done", "dropped"}:
                self.items[ident]["status"] = "active"
                self.items[ident]["active_round"] = round_id
        self.save()
        self._round_files(record)
        lock.update(
            phase="active",
            resumed_at=record["resumed_at"],
            resume_count=record["resume_count"],
            resumed_by_pid=os.getpid(),
            host=socket.gethostname(),
        )
        self.replace_lock(lock)
        self.append_event("round_resumed", round_id=round_id, resume_count=record["resume_count"])
        return record

    def note(
        self,
        text: str,
        next_action: str = "",
        kind: str = "checkpoint",
        item: str | None = None,
    ) -> dict[str, Any]:
        _, record = self.active_round()
        if item:
            item = item.upper()
            if item not in record["items"]:
                raise HarnessError(f"{item} is not active in {record['round_id']}")
        stamp = now()
        entry = {"at": stamp, "kind": kind, "text": text.strip(), "next": next_action.strip(), "item": item}
        if not entry["text"]:
            raise HarnessError("note text cannot be empty")
        record["last_note"] = entry
        self.save()
        directory = self.root / record["workdir"]
        with (directory / "NOTES.md").open("a", encoding="utf-8") as stream:
            label = f" [{item}]" if item else ""
            stream.write(f"\n## {stamp} — {kind}{label}\n\n{entry['text']}\n")
            if entry["next"]:
                stream.write(f"\nNext: {entry['next']}\n")
            stream.flush()
            os.fsync(stream.fileno())
        if entry["next"]:
            with (directory / "NEXT.md").open("a", encoding="utf-8") as stream:
                stream.write(f"\n- {stamp}: {entry['next']}\n")
                stream.flush()
                os.fsync(stream.fileno())
        self.append_event(
            "note",
            round_id=record["round_id"],
            note_kind=entry["kind"],
            text=entry["text"],
            next=entry["next"],
            item=entry["item"],
            note_at=entry["at"],
        )
        return entry

    def transition(self, identities: list[str], status: str, reason: str = "") -> None:
        if status not in STATUSES:
            raise HarnessError(f"invalid status: {status}")
        if status in {"blocked", "dropped"} and not reason.strip():
            raise HarnessError(f"{status.removesuffix('ed')}ing an item requires --reason")
        for raw in identities:
            ident = raw.upper()
            if ident not in self.items:
                raise HarnessError(f"unknown project item: {ident}")
            item = self.items[ident]
            if status == "done" and any(
                self.items.get(dep, {}).get("status") not in {"done", "dropped"}
                for dep in item["depends"]
            ):
                raise HarnessError(f"{ident} cannot be done before all dependencies are done")
            item["status"] = status
            item["updated_at"] = now()
            if status == "blocked":
                item["blocked_reason"] = reason.strip()
            else:
                item.pop("blocked_reason", None)
            if status == "dropped":
                item["dropped_reason"] = reason.strip()
            else:
                item.pop("dropped_reason", None)
            if status == "done":
                item["completed_at"] = now()
            else:
                item.pop("completed_at", None)
            if status not in {"active", "blocked"}:
                item["active_round"] = None
        self.save()
        self.append_event("item_transition", items=[item.upper() for item in identities], status=status, reason=reason)

    def close_round(self, summary: str, done: list[str]) -> dict[str, Any]:
        if not summary.strip():
            raise HarnessError("round close summary cannot be empty")
        _, record = self.active_round()
        declared_done = {ident.upper() for ident in done}
        unknown = declared_done - set(record["items"])
        if unknown:
            raise HarnessError(f"cannot close unrelated items: {', '.join(sorted(unknown))}")
        for ident in sorted(declared_done):
            unresolved = [
                dependency
                for dependency in self.items[ident]["depends"]
                if self.items.get(dependency, {}).get("status") not in {"done", "dropped"}
                and dependency not in declared_done
            ]
            if unresolved:
                raise HarnessError(
                    f"{ident} cannot be done before dependencies are settled: {', '.join(unresolved)}"
                )
        stamp = now()
        for ident in sorted(declared_done):
            item = self.items[ident]
            item["status"] = "done"
            item["active_round"] = None
            item["completed_at"] = stamp
            item["updated_at"] = stamp
            item.pop("blocked_reason", None)
            item.pop("dropped_reason", None)
        for ident in record["items"]:
            item = self.items[ident]
            if item["status"] == "active":
                item["status"] = "pending"
                item["active_round"] = None
                item["updated_at"] = now()
        record["status"] = "closed"
        record["closed_at"] = stamp
        record["summary"] = summary.strip()
        self.register["active_round"] = None
        self.save()
        directory = self.root / record["workdir"]
        with (directory / "RESULTS.md").open("a", encoding="utf-8") as stream:
            stream.write(f"\n## Close — {record['closed_at']}\n\n{summary.strip() or 'No result summary supplied.'}\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.append_event(
            "round_closed", round_id=record["round_id"], summary=summary.strip(), done=sorted(declared_done)
        )
        # Remove last: if anything above fails, the recovery handle remains.
        self.release_lock()
        return record

    def bootstrap(self, fields: dict[str, str]) -> None:
        project = self.register.setdefault("project", {})
        project.update({key: value.strip() for key, value in fields.items() if value.strip()})
        required = ("title", "question", "falsifier", "deliverable")
        project["status"] = "active" if all(project.get(key) for key in required) else "bootstrap"
        project["updated_at"] = now()
        self.save()
        self.append_event("bootstrap", fields=sorted(key for key, value in fields.items() if value.strip()))

    def event_tail(self, count: int = 5) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.events_path.read_text(encoding="utf-8").splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
        return events[-count:]

    def validate(self, include_lock: bool = True) -> list[str]:
        errors: list[str] = []
        if self.register.get("schema_version") != 1:
            errors.append("register schema_version must be 1")
        if not isinstance(self.items, dict) or not isinstance(self.rounds, dict):
            return errors + ["items and rounds must be objects"]
        for ident, item in self.items.items():
            if not ITEM_ID.fullmatch(ident):
                errors.append(f"invalid item ID: {ident}")
                continue
            if item.get("status") not in STATUSES:
                errors.append(f"{ident}: invalid status {item.get('status')!r}")
            if item.get("mode") not in MODES:
                errors.append(f"{ident}: invalid mode {item.get('mode')!r}")
            if item.get("stage") not in self.stages:
                errors.append(f"{ident}: invalid stage {item.get('stage')!r}")
            for dependency in item.get("depends", []):
                if dependency not in self.items:
                    errors.append(f"{ident}: missing dependency {dependency}")
                if dependency == ident:
                    errors.append(f"{ident}: self dependency")
            if item.get("status") == "done":
                unresolved = [
                    dependency
                    for dependency in item.get("depends", [])
                    if self.items.get(dependency, {}).get("status") not in {"done", "dropped"}
                ]
                if unresolved:
                    errors.append(
                        f"{ident}: done before dependencies are settled: {', '.join(unresolved)}"
                    )
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(ident: str, path: list[str]) -> None:
            if ident in visiting:
                errors.append("dependency cycle: " + " -> ".join(path + [ident]))
                return
            if ident in visited or ident not in self.items:
                return
            visiting.add(ident)
            for dependency in self.items[ident].get("depends", []):
                visit(dependency, path + [ident])
            visiting.remove(ident)
            visited.add(ident)

        for ident in self.items:
            visit(ident, [])
        active_id = self.register.get("active_round")
        if active_id and active_id not in self.rounds:
            errors.append(f"active round {active_id} is missing")
        if include_lock:
            try:
                lock = self.read_lock()
            except HarnessError as exc:
                errors.append(str(exc))
                lock = None
            if bool(lock) != bool(active_id):
                errors.append("round lock and register active_round disagree")
            if lock and active_id and lock.get("round_id") != active_id:
                errors.append("round lock names a different active round")
        return list(dict.fromkeys(errors))

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(self.register, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
