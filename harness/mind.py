from __future__ import annotations

import difflib
import json
from pathlib import Path
import sys
from typing import Any


class MindError(RuntimeError):
    pass


def load_index(root: Path) -> dict[str, Any]:
    path = root / ".mind/index.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MindError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise MindError(".mind/index.json must have schema_version 1")
    if not isinstance(value.get("topics"), dict) or not value["topics"]:
        raise MindError(".mind/index.json has no topics")
    return value


def _topic_lookup(index: dict[str, Any]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for name, record in index["topics"].items():
        if not isinstance(record, dict):
            raise MindError(f"{name}: topic entry must be an object")
        key = name.casefold()
        if key in lookup:
            raise MindError(f"duplicate mind topic or alias: {name}")
        lookup[key] = name
        aliases = record.get("aliases", [])
        if not isinstance(aliases, list):
            raise MindError(f"{name}: aliases must be a list")
        for alias in aliases:
            key = str(alias).casefold()
            if not key or key in lookup:
                raise MindError(f"duplicate mind topic or alias: {alias}")
            lookup[key] = name
    return lookup


def validate_index(root: Path, index: dict[str, Any] | None = None) -> list[str]:
    index = index or load_index(root)
    failures: list[str] = []
    try:
        lookup = _topic_lookup(index)
    except MindError as exc:
        failures.append(str(exc))
        lookup = {}
    hot_limit = index.get("hot_max_bytes")
    more_limit = index.get("more_max_bytes")
    if not isinstance(hot_limit, int) or hot_limit < 100:
        failures.append("hot_max_bytes must be an integer of at least 100")
    if not isinstance(more_limit, int) or more_limit < 100:
        failures.append("more_max_bytes must be an integer of at least 100")
    for name, record in index["topics"].items():
        if not isinstance(record, dict):
            failures.append(f"{name}: topic entry must be an object")
            continue
        full = record.get("full")
        if not isinstance(full, list) or not full or not all(isinstance(path, str) for path in full):
            failures.append(f"{name}: full must be a nonempty path list")
        for tier, limit in (("hot", hot_limit), ("more", more_limit)):
            relative = record.get(tier)
            if not isinstance(relative, str):
                failures.append(f"{name}: missing {tier} path")
                continue
            path = (root / relative).resolve()
            if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
                failures.append(f"{name}: {tier} path leaves the repository")
                continue
            try:
                data = path.read_bytes()
                text = data.decode("utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                failures.append(f"{name}: cannot read {tier}: {exc}")
                continue
            if isinstance(limit, int) and len(data) > limit:
                failures.append(f"{name}: {tier} is {len(data)} bytes; limit is {limit}")
            if tier == "hot":
                suffix = f"MORE ./mind how {name} more\n".encode()
            else:
                paths = full if isinstance(full, list) else []
                suffix = ("FULL " + " ".join(paths) + "\n").encode()
            rendered_size = len(data) + len(suffix)
            if isinstance(limit, int) and rendered_size > limit:
                failures.append(
                    f"{name}: rendered {tier} is {rendered_size} bytes; limit is {limit}"
                )
            if not text.endswith("\n"):
                failures.append(f"{name}: {tier} must end with one newline")
            if "\n\n" in text:
                failures.append(f"{name}: {tier} contains excess blank lines")
            if text.lstrip().startswith("#"):
                failures.append(f"{name}: {tier} must not use a decorative heading")
        for relative in full if isinstance(full, list) else []:
            path = (root / relative).resolve()
            if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
                failures.append(f"{name}: cold path leaves the repository: {relative}")
            elif not path.is_file():
                failures.append(f"{name}: missing cold document {relative}")
    if len(lookup) < len(index["topics"]):
        failures.append("mind lookup is incomplete")
    return failures


def render(root: Path, topic: str, more: bool = False) -> str:
    index = load_index(root)
    lookup = _topic_lookup(index)
    key = topic.casefold()
    if key not in lookup:
        suggestion = difflib.get_close_matches(key, sorted(lookup), n=1)
        suffix = f"; nearest={suggestion[0]}" if suggestion else ""
        raise MindError(f"unknown topic {topic!r}{suffix}")
    canonical = lookup[key]
    record = index["topics"][canonical]
    tier = "more" if more else "hot"
    relative = record.get(tier)
    if not isinstance(relative, str):
        raise MindError(f"{canonical}: missing {tier} path")
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root):
        raise MindError(f"{canonical}: {tier} path leaves the repository")
    try:
        text = path.read_text(encoding="utf-8").rstrip("\n")
    except OSError as exc:
        raise MindError(f"{canonical}: cannot read {tier}: {exc}") from exc
    if more:
        full = record.get("full")
        if not isinstance(full, list) or not full or not all(isinstance(item, str) for item in full):
            raise MindError(f"{canonical}: full must be a nonempty path list")
        rendered = text + "\nFULL " + " ".join(full)
    else:
        rendered = text + f"\nMORE ./mind how {canonical} more"
    limit = index.get("more_max_bytes" if more else "hot_max_bytes")
    if not isinstance(limit, int) or len((rendered + "\n").encode()) > limit:
        raise MindError(f"{canonical}: rendered {tier} exceeds its byte budget")
    return rendered


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    root = (root or Path.cwd()).resolve()
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0].casefold() == "audit":
        try:
            failures = validate_index(root)
        except MindError as exc:
            failures = [str(exc)]
        if failures:
            print("MIND AUDIT failed")
            for failure in failures:
                print(failure)
            return 1
        print("MIND AUDIT passed")
        return 0
    if args and args[0].casefold() == "how":
        args.pop(0)
    try:
        index = load_index(root)
        if not args:
            print("USAGE ./mind how TOPIC [more]")
            print("TOPICS " + " ".join(index["topics"]))
            return 0
        if len(args) > 2 or (len(args) == 2 and args[1].casefold() != "more"):
            raise MindError("use exactly ./mind how TOPIC or ./mind how TOPIC more")
        print(render(root, args[0], more=len(args) == 2))
        return 0
    except MindError as exc:
        print(f"mind: {exc}", file=sys.stderr)
        return 2
