# Operations reference

## High-frequency commands

| Command | Effect |
|---|---|
| `./h` | Print the compact recovery card |
| `./h advance TAG...` | Open one advancement round on ready matching items |
| `./h refine TAG...` | Open one refinement round on ready matching items |
| `./h note TEXT --next TEXT` | Persist a checkpoint and exact resume action |
| `./h close --summary TEXT --done P...` | Close the round and optionally complete active items |
| `./h recover` | Print open-round recovery state and next recovery command |
| `./h resume` | Reconcile and reaffirm an interrupted round |
| `./h report` | Print the macro lifecycle report |
| `./h report --json` | Print compact structured state for a model or script |
| `./h run --label NAME -- COMMAND...` | Run one lowered-priority command with the global lock and watchdog |
| `./h run-status` | Show the active/stale compute lock or unresolved last run |

## Planning and state

`./h register PLAN.md` parses all Markdown task lines. `./h register --text
'- [ ] ...'` integrates a small addition without opening an editor. Use
`./h block P001 --reason TEXT`, `./h reopen P001`, and `./h done P001` for
explicit transitions. Use `./h drop P001 --reason TEXT` when an optional or
superseded item does not apply; its identity remains and dependents may proceed.

Do not hand-edit the JSON register in ordinary work. If manual disaster recovery
is unavoidable, copy the file first, make the smallest correction, run
`./h doctor`, regenerate reports, and record the intervention in the current
round notes.

## Verification

`./h doctor` is structural and fast. `./h check` runs checks marked default in
`.harness/config.json`. `./h check --all` also runs optional paper and formal
builds; install their toolchains first. Commands are stored as argument arrays,
not shell strings. Every configured check is itself run through the resource
guard.

## Local computation

Follow `docs/RESOURCE_SAFETY.md`. Material commands must use `./h run`; the
default and maximum timeout is 240 seconds and default nice level is 10. The
runner also limits common hidden numerical thread pools to one and refuses a
second run while its global compute lock is live. Do not put secrets in command
arguments because the recovery record preserves them.

On timeout, the runner terminates the complete process group, records a brief
system process audit, and exits 124. Run `./h run-status`. If another process was
the likely source of contention, wait or coordinate. Otherwise change the
representation, scale, import surface, or checkpoint boundary before retrying.
Do not raise the ceiling.

The default project policy audit checks that the Lean and release control files
exist and rejects placeholders, custom axioms/constants, and unsafe Lean
declarations. The paper build separately checks its TeX log, metadata, and font
embedding. Neither automated check replaces the full replay, theorem-statement
comparison, or page-by-page rendered PDF inspection required at release.

## Recovery cases

### The model or terminal stopped mid-round

Run `./h recover`, inspect the reported work directory, then `./h resume`. Continue
from the `NEXT` line. This does not create a new round.

### Start failed after creating a provisional lock

Run `./h resume`. It reconstructs the round from the lock, reconciles selected
items, and creates any missing round template files.

### Lock and register disagree

Run `./h doctor` and preserve both files. Do not delete either. Use the round ID,
event tail, and work directory to determine the last completed write. The close
algorithm removes the lock last, so a lock normally means recovery is safer than
rollback.

### Generated status is stale

Run `./h report --write`. `STATUS.md` and `NEXT.md` are disposable projections;
the register and work records are authoritative.

### A computation was cut off

Run `./h run-status`. If the compute lock is active, do not start a replacement;
the recorded controller or child is alive. A stale lock is recoverable by the
next guarded invocation only after both recorded PIDs are dead. A timeout or
interruption remains visible in the bare `./h` recovery card until a later
guarded run completes.

## Git boundary

The harness never commits or pushes. Version-control publication is intentionally
outside the research-state machine so a user can review scope. Before a commit,
run `./h doctor`, the relevant checks, and inspect `git diff --check` plus the
full staged diff. Never commit `.harness/round.lock`.
