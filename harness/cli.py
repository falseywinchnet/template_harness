from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .context import handoff_status, render_handoff, save_handoff
from .parser import PlanParseError, parse_plan, parse_plan_text
from .reports import formal_claims, full_report, recovery_brief, write_reports
from .runtime import (
    DEFAULT_NICE,
    DEFAULT_SECONDS,
    RuntimeControlError,
    run_guarded,
    runtime_brief,
    runtime_snapshot,
)
from .store import HarnessError, Store, atomic_text


BOOTSTRAP_QUESTIONS = """Bootstrap interview

1. What is the project title and research field?
2. What exact question should the project answer?
3. What is the initial hypothesis, if one exists?
4. What observation or result would falsify or materially weaken it?
5. What is the intended deliverable and audience (paper, note, dataset, proof, software)?
6. What constraints, non-goals, deadline, and required methods or formal systems apply?
7. What evidence already exists locally, and where is it?
8. What data or parameter scale, compute budget, runtime limit, and interruption
   recovery requirements should shape the method?
9. What raw, independently constructible instance lies inside the target domain,
   and what strictness or nondegeneracy keeps it off the boundary?
10. If this is a containment or invariant claim, what separately establishes
    object identity, initialization, preservation, and reachability?
11. What model time/cost per round is acceptable, what context window is
    verified, and how much context should remain when a manual handoff begins?

After the answers, run `./h bootstrap` with the core fields, tailor PLAN.md, then
run `./h register PLAN.md`. See docs/BOOTSTRAP.md for Sol's exact procedure.
"""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="h",
        description="Durable scientific-project register. Bare ./h prints the recovery card.",
    )
    commands = result.add_subparsers(dest="command")

    boot = commands.add_parser("bootstrap", help="show intake questions or record the project charter")
    boot.add_argument("--title")
    boot.add_argument("--field", default="")
    boot.add_argument("--question")
    boot.add_argument("--hypothesis", default="")
    boot.add_argument("--falsifier")
    boot.add_argument("--deliverable")
    boot.add_argument("--audience", default="")
    boot.add_argument("--constraints", default="")
    boot.add_argument("--formalization", default="")
    boot.add_argument("--compute", default="")
    boot.add_argument("--interior", default="")
    boot.add_argument("--containment", default="")
    boot.add_argument("--model-budget", default="")
    boot.add_argument("--context-reserve", default="")

    register = commands.add_parser("register", help="integrate Markdown task lines into the register")
    register.add_argument("source", nargs="?", help="Markdown file, or '-' for stdin")
    register.add_argument("--text", help="register one or more literal Markdown task lines")

    for mode in ("advance", "refine"):
        start = commands.add_parser(mode, help=f"open one exclusive {mode} round")
        start.add_argument("tags", nargs="*", help="tags or P item IDs; comma-separated is accepted")

    note = commands.add_parser("note", aliases=["checkpoint"], help="write a crash-safe round checkpoint")
    note.add_argument("text")
    note.add_argument("--next", dest="next_action", default="")
    note.add_argument("--kind", choices=["checkpoint", "decision", "result", "failure"], default="checkpoint")
    note.add_argument("--item")

    close = commands.add_parser("close", help="close the active round and release the global lock")
    close.add_argument("--summary", required=True)
    close.add_argument("--done", nargs="*", default=[])

    commands.add_parser("recover", help="print the exact open-round recovery state")
    commands.add_parser("resume", help="repair/reaffirm the open round after interruption")

    context = commands.add_parser("context", help="show or save the compact manual handoff")
    context_commands = context.add_subparsers(dest="context_command")
    save_context = context_commands.add_parser("save", help="write a bounded intent handoff")
    save_context.add_argument("--state", required=True)
    save_context.add_argument("--next", dest="next_action", required=True)
    save_context.add_argument("--why", default="")
    save_context.add_argument("--files", default="")
    save_context.add_argument("--risks", default="")
    save_context.add_argument("--verify", default="")
    context_commands.add_parser("check", help="fail if the manual handoff is missing or stale")

    report = commands.add_parser("report", aliases=["status"], help="print project-wide progress")
    report.add_argument("--json", action="store_true", dest="as_json")
    report.add_argument("--write", action="store_true")

    done = commands.add_parser("done", help="mark project items complete")
    done.add_argument("items", nargs="+")
    block = commands.add_parser("block", help="mark project items blocked")
    block.add_argument("items", nargs="+")
    block.add_argument("--reason", required=True)
    reopen = commands.add_parser("reopen", help="return items to pending")
    reopen.add_argument("items", nargs="+")
    drop = commands.add_parser("drop", help="retire optional or superseded items without erasing them")
    drop.add_argument("items", nargs="+")
    drop.add_argument("--reason", required=True)

    commands.add_parser("doctor", help="validate state, dependencies, lock, and required files")
    check = commands.add_parser("check", help="run configured shell-free verification commands")
    check.add_argument("--all", action="store_true", dest="run_all")
    run = commands.add_parser("run", help="run one nice, exclusive, watchdog-bounded command")
    run.add_argument("--timeout", type=int, default=DEFAULT_SECONDS)
    run.add_argument("--nice", type=int, default=DEFAULT_NICE, dest="nice_level")
    run.add_argument("--label", default="ad-hoc")
    run.add_argument("--cwd", default=".")
    run.add_argument("argv", nargs=argparse.REMAINDER)
    run_status = commands.add_parser("run-status", help="show the compute lock and last guarded run")
    run_status.add_argument("--json", action="store_true", dest="as_json")
    return result


def _project_markdown(fields: dict[str, str]) -> str:
    return f"""# {fields['title']}

## Research question

{fields['question']}

## Initial hypothesis

{fields.get('hypothesis') or 'No directional hypothesis has been adopted yet.'}

## Falsification boundary

{fields['falsifier']}

## Objective target interior

{fields.get('interior') or 'Construct a raw admissible instance and prove its result and nondegeneracy independently.'}

## Containment and invariant boundary

{fields.get('containment') or 'Not applicable unless the claim involves membership, invariance, or generated-state containment.'}

## Deliverable

{fields['deliverable']}

## Field and audience

- Field: {fields.get('field') or 'To be specified'}
- Audience: {fields.get('audience') or 'To be specified'}

## Constraints and non-goals

{fields.get('constraints') or 'To be specified.'}

## Formalization and verification

{fields.get('formalization') or 'Use the lightest verification boundary that supports the claims.'}

## Computational scale and resources

{fields.get('compute') or 'Estimate scale, arithmetic, runtime, memory, and recovery requirements before implementing a material computation.'}

## Model-round economy

- Time and cost: {fields.get('model_budget') or 'Measure round duration and cost; split work when a bounded decision can be reached more cheaply.'}
- Context reserve: {fields.get('context_reserve') or 'Verify the active model window; default to a manual handoff when 30% remains or before a large phase.'}

## Evidence locations

- `sources/` — preserved external inputs
- `research/` — target, dependencies, claims, and evidence map
- `computations/` — algorithm contract, benchmarks, and replay manifests
- `work/` — immutable round records and experiments
- `paper/` — maintained manuscript and release package
"""


def _json_report(store: Store) -> dict[str, object]:
    context_status, context_reasons = handoff_status(store)
    return {
        "project": store.register.get("project", {}),
        "active_round": store.register.get("active_round"),
        "lock": store.read_lock(),
        "ready": store.ready(),
        "blocked": [ident for ident, item in store.items.items() if item["status"] == "blocked"],
        "counts": {
            status: sum(item["status"] == status for item in store.items.values())
            for status in ("pending", "active", "blocked", "done", "dropped")
        },
        "register_digest": store.digest(),
        "context": {"status": context_status, "reasons": context_reasons},
        "formal_claims": formal_claims(store.root),
    }


def _doctor(store: Store) -> list[str]:
    errors = store.validate()
    required = [
        "README.md",
        "AGENTS.md",
        "PROJECT.md",
        "PLAN.md",
        "docs/BOOTSTRAP.md",
        "docs/SPECIFICATION.md",
        "docs/LEAN_ENGINEERING.md",
        "docs/LEAN_CLAIM_STANDARD.md",
        "docs/COMPUTE_DESIGN.md",
        "docs/PYTHON_COMPUTATION.md",
        "docs/PAPER_NARRATIVE.md",
        "docs/PDF_HOUSE_STYLE.md",
        "docs/RESOURCE_SAFETY.md",
        "docs/CONTEXT_ECONOMY.md",
        "harness/runtime.py",
        "harness/context.py",
        "harness/mind.py",
        "mind",
        ".mind/index.json",
        ".harness/context.json",
        ".codex/config.toml",
        ".codex/hooks.json",
        "scripts/context_hook.py",
        "work/ROUND_TEMPLATE.md",
        "research/TARGET.md",
        "computations/COMPUTE_PLAN.md",
        "computations/requirements-sympy.txt",
        "formal/AXIOMS.md",
        "formal/CLAIMS.json",
        "formal/Formal/ClaimContract.lean",
        "paper/RELEASE_MANIFEST.md",
        "paper/EDITORIAL_AUDIT.md",
        "scripts/audit_manuscript.py",
    ]
    for relative in required:
        if not (store.root / relative).is_file():
            errors.append(f"missing required template file: {relative}")
    if store.events_path.exists():
        for number, line in enumerate(store.events_path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"events.jsonl line {number} is not valid JSON")
    return errors


def _run_checks(store: Store, run_all: bool) -> None:
    checks = store.config.get("checks", [])
    selected = [check for check in checks if check.get("default") or run_all]
    if not selected:
        print("No checks selected.")
        return
    for check in selected:
        command = check.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            raise HarnessError(f"invalid shell-free check definition: {check!r}")
        cwd = store.root / check.get("cwd", ".")
        print(f"CHECK {check.get('name', command[0])}")
        return_code = run_guarded(
            store.root,
            command,
            cwd=cwd,
            label=f"check:{check.get('name', command[0])}",
        )
        if return_code:
            raise HarnessError(f"check failed: {check.get('name', command[0])}")


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        argv[0] = argv[0].casefold()
    args = parser().parse_args(argv)
    try:
        store = Store(root or Path.cwd())
        if not args.command:
            print(recovery_brief(store))
            context_status, context_reasons = handoff_status(store)
            detail = " · " + "; ".join(context_reasons) if context_reasons else ""
            print(f"CONTEXT  {context_status}{detail}")
            compute = runtime_brief(store.root)
            if compute:
                print(compute)
            return 0
        command = args.command.casefold()
        if command == "bootstrap":
            core = (args.title, args.question, args.falsifier, args.deliverable)
            if not any(core):
                print(BOOTSTRAP_QUESTIONS.rstrip())
                return 0
            if not all(core):
                raise HarnessError("bootstrap recording requires --title, --question, --falsifier, and --deliverable")
            fields = {
                key: value or ""
                for key, value in vars(args).items()
                if key not in {"command"}
            }
            atomic_text(store.root / "PROJECT.md", _project_markdown(fields))
            store.bootstrap(fields)
            write_reports(store)
            print("Bootstrap charter recorded in PROJECT.md. Tailor PLAN.md, then run ./h register PLAN.md.")
        elif command == "register":
            if bool(args.source) == bool(args.text):
                raise HarnessError("provide exactly one source file/stdin or --text")
            if args.text:
                parsed = parse_plan_text(args.text)
                source = "command text"
            elif args.source == "-":
                parsed = parse_plan_text(sys.stdin.read())
                source = "stdin"
            else:
                path = (store.root / args.source).resolve()
                parsed = parse_plan(path)
                try:
                    source = str(path.relative_to(store.root))
                except ValueError:
                    source = str(path)
            created, updated = store.register_items(parsed, source)
            write_reports(store)
            print(f"REGISTERED created={len(created)} updated={len(updated)}")
            if created:
                print("CREATED " + " ".join(created))
            if updated:
                print("UPDATED " + " ".join(updated))
        elif command in {"advance", "refine"}:
            record = store.start_round(command, args.tags)
            write_reports(store)
            print(
                f"OPEN {record['round_id']} mode={record['mode']} items={' '.join(record['items'])} "
                f"workdir={record['workdir']}"
            )
        elif command in {"note", "checkpoint"}:
            entry = store.note(args.text, args.next_action, args.kind, args.item)
            write_reports(store)
            print(f"NOTED {entry['at']} kind={entry['kind']}")
        elif command == "close":
            record = store.close_round(args.summary, args.done)
            write_reports(store)
            print(f"CLOSED {record['round_id']} done={' '.join(args.done) or 'none'}")
        elif command == "recover":
            print(recovery_brief(store))
            context_status, context_reasons = handoff_status(store)
            detail = " · " + "; ".join(context_reasons) if context_reasons else ""
            print(f"CONTEXT  {context_status}{detail}")
            compute = runtime_brief(store.root)
            if compute:
                print(compute)
            if store.read_lock():
                print("ACTION   Run ./h resume, then continue from NEXT in the round directory.")
        elif command == "resume":
            record = store.resume_round()
            write_reports(store)
            if record.get("recovery_action") == "finalized_close":
                print(f"RECOVERED {record['round_id']} finalized=close lock=released")
            else:
                print(f"RESUMED {record['round_id']} workdir={record['workdir']}")
        elif command == "context":
            if args.context_command == "save":
                if store.read_lock():
                    store.note(args.state, args.next_action)
                    write_reports(store)
                save_handoff(
                    store,
                    {
                        "state": args.state,
                        "next": args.next_action,
                        "why": args.why,
                        "files": args.files,
                        "risks": args.risks,
                        "verify": args.verify,
                    },
                )
                print(render_handoff(store))
            elif args.context_command == "check":
                status, reasons = handoff_status(store)
                print(f"HANDOFF {status}" + (" " + "; ".join(reasons) if reasons else ""))
                if status != "FRESH":
                    return 1
            else:
                print(render_handoff(store))
        elif command in {"report", "status"}:
            if args.write:
                paths = write_reports(store)
                print("WROTE " + " ".join(str(path.relative_to(store.root)) for path in paths))
            elif args.as_json:
                print(json.dumps(_json_report(store), indent=2, sort_keys=True))
            else:
                print(full_report(store), end="")
        elif command == "done":
            store.transition(args.items, "done")
            write_reports(store)
            print("DONE " + " ".join(item.upper() for item in args.items))
        elif command == "block":
            store.transition(args.items, "blocked", args.reason)
            write_reports(store)
            print("BLOCKED " + " ".join(item.upper() for item in args.items))
        elif command == "reopen":
            store.transition(args.items, "pending")
            write_reports(store)
            print("REOPENED " + " ".join(item.upper() for item in args.items))
        elif command == "drop":
            store.transition(args.items, "dropped", args.reason)
            write_reports(store)
            print("DROPPED " + " ".join(item.upper() for item in args.items))
        elif command == "doctor":
            errors = _doctor(store)
            if errors:
                print("DOCTOR failed")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"DOCTOR ok register={store.digest()[:16]} items={len(store.items)} rounds={len(store.rounds)}")
        elif command == "check":
            _run_checks(store, args.run_all)
            print("CHECKS passed")
        elif command == "run":
            argv = list(args.argv)
            if argv and argv[0] == "--":
                argv.pop(0)
            return run_guarded(
                store.root,
                argv,
                cwd=store.root / args.cwd,
                label=args.label,
                timeout_seconds=args.timeout,
                nice_level=args.nice_level,
            )
        elif command == "run-status":
            snapshot = runtime_snapshot(store.root)
            if args.as_json:
                print(json.dumps(snapshot, indent=2, sort_keys=True))
            else:
                brief = runtime_brief(store.root)
                print(brief or "COMPUTE idle; no unresolved guarded run")
        return 0
    except (HarnessError, PlanParseError, RuntimeControlError) as exc:
        print(f"h: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
