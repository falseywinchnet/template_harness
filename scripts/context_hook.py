#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.context import handoff_status, render_handoff  # noqa: E402
from harness.store import HarnessError, Store  # noqa: E402


def response(**fields: object) -> None:
    print(json.dumps({"continue": True, "suppressOutput": False, **fields}))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        response(systemMessage="CONTEXT HOOK could not read its event; run ./h context manually")
        return 0
    event = str(payload.get("hook_event_name", ""))
    trigger = str(payload.get("trigger") or payload.get("compact_trigger") or "unknown")
    try:
        store = Store(ROOT)
        status, reasons = handoff_status(store)
        handoff = render_handoff(store)
    except HarnessError as exc:
        response(systemMessage=f"CONTEXT HOOK unavailable: {exc}; run ./h context manually")
        return 0
    if event == "PreCompact":
        if trigger == "manual" and status != "FRESH":
            print(
                json.dumps(
                    {
                        "continue": False,
                        "stopReason": "Manual compaction requires a fresh ./h context save handoff",
                        "systemMessage": (
                            "CONTEXT GATE stopped manual compaction. Run ./h context, then "
                            "./h context save --state ... --next ... before /compact. "
                            + "; ".join(reasons)
                        ),
                        "suppressOutput": False,
                    }
                )
            )
            return 0
        if status == "FRESH":
            response(
                systemMessage=(
                    "CONTEXT GATE preserve this manual operational handoff exactly; "
                    "it outranks smooth transcript summary:\n" + handoff
                )
            )
        else:
            response(
                systemMessage=(
                    "CONTEXT GATE auto-compaction reached a missing/stale manual handoff. "
                    "Continue to avoid hard-limit failure; after compaction run ./h context and "
                    "reconstruct only from durable state."
                )
            )
        return 0
    if event in {"PostCompact", "SessionStart"}:
        message = (
            "CONTEXT REENTRY run ./h context before other work. Treat inferred continuity "
            "from the compacted transcript as provisional; execute recorded NEXT only after "
            "checking stale warnings."
        )
        if event == "SessionStart":
            print(
                json.dumps(
                    {
                        "continue": True,
                        "systemMessage": message,
                        "suppressOutput": False,
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": (
                                "DURABLE CONTEXT REENTRY\n" + handoff + "\n" + message
                            ),
                        },
                    }
                )
            )
        else:
            response(systemMessage=message)
        return 0
    response()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
