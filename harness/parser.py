from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


TASK = re.compile(
    r"^\s*-\s*\[(?P<mark>[ xX!~])\]\s*"
    r"(?:(?P<id>P\d{3,6})\s*(?:[|:\-—]\s*)?)?(?P<body>.+?)\s*$"
)
FIELD = re.compile(r"^(?P<key>[A-Za-z][A-Za-z_-]*)\s*[:=]\s*(?P<value>.*)$")


class PlanParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedItem:
    ident: str | None
    title: str
    stage: str
    mode: str
    tags: tuple[str, ...]
    depends: tuple[str, ...]
    acceptance: str
    reason: str
    status: str
    line: int


def _tokens(value: str) -> tuple[str, ...]:
    if value.strip().casefold() in {"", "-", "none"}:
        return ()
    return tuple(
        dict.fromkeys(
            token.strip().removeprefix("#").casefold()
            for token in re.split(r"[,\s]+", value)
            if token.strip()
        )
    )


def parse_plan_text(text: str) -> list[ParsedItem]:
    items: list[ParsedItem] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TASK.match(line)
        if not match:
            continue
        segments = [part.strip() for part in match.group("body").split("|")]
        title = segments[0]
        if not title:
            raise PlanParseError(f"line {line_number}: task title is empty")
        fields: dict[str, str] = {}
        for segment in segments[1:]:
            parsed = FIELD.match(segment)
            if not parsed:
                raise PlanParseError(
                    f"line {line_number}: expected key=value after '|', got {segment!r}"
                )
            key = parsed.group("key").replace("-", "_").casefold()
            fields[key] = parsed.group("value").strip()
        stage = fields.get("stage", "analysis").casefold()
        mode = fields.get("mode", "either").casefold()
        if mode not in {"advance", "refine", "either"}:
            raise PlanParseError(f"line {line_number}: invalid mode {mode!r}")
        mark = match.group("mark")
        status = {"x": "done", "X": "done", "!": "blocked", "~": "dropped"}.get(
            mark, "pending"
        )
        depends = _tokens(fields.get("depends", fields.get("after", "")))
        invalid = [item for item in depends if not re.fullmatch(r"p\d{3,6}", item)]
        if invalid:
            raise PlanParseError(
                f"line {line_number}: dependencies must be P items: {', '.join(invalid)}"
            )
        items.append(
            ParsedItem(
                ident=match.group("id").upper() if match.group("id") else None,
                title=title,
                stage=stage,
                mode=mode,
                tags=_tokens(fields.get("tags", "")),
                depends=tuple(item.upper() for item in depends),
                acceptance=fields.get("accept", fields.get("acceptance", "")).strip(),
                reason=fields.get("reason", "").strip(),
                status=status,
                line=line_number,
            )
        )
    if not items:
        raise PlanParseError("no Markdown task lines found; use '- [ ] P001 | title | key=value'")
    return items


def parse_plan(path: Path) -> list[ParsedItem]:
    try:
        return parse_plan_text(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PlanParseError(f"cannot read {path}: {exc}") from exc
