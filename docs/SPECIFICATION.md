# Harness specification

Version: 1.1

This document is normative for the local command, register, lock, and generated
reports. Documentation examples may be friendlier; when they disagree with this
file, this file wins.

## 1. Objects

### 1.1 Project item

A project item has a stable `P` identity, title, lifecycle stage, round mode,
tags, zero or more dependency IDs, acceptance text, source location, and runtime
status. Valid statuses are `pending`, `active`, `blocked`, `done`, and `dropped`.
Valid modes are `advance`, `refine`, and `either`.

`done` means the acceptance text is satisfied, not merely that an attempt ended.
`blocked` and `dropped` require recorded reasons. `dropped` preserves identity
and history while settling an optional dependency.

### 1.2 Round

A round has a stable `R` identity, one mode, selected items, tags, timestamps,
status, resume count, work directory, and latest checkpoint. A round is the unit
of recoverable scientific attention. Exactly zero or one round may be open.

### 1.3 Event

Every register mutation appends one JSON object to `.harness/events.jsonl`.
Events are an audit trail, not canonical state. Canonical current state is
`.harness/register.json`; round artifacts are canonical narrative evidence.

## 2. Markdown registration grammar

The parser accepts Markdown checkbox lines:

```text
- [MARK] [PID] TITLE [| KEY=VALUE ...]
```

- `MARK`: space, `x`, `X`, `!`, or `~` for pending, done, blocked, or dropped.
- `PID`: optional `P` followed by 3–6 digits.
- supported keys: `stage`, `mode`, `tags`, `depends`/`after`,
  `accept`/`acceptance`, and `reason` for a new blocked or dropped item.
- tags and dependencies are comma- or whitespace-separated.
- absent IDs are allocated monotonically.
- absent stage and mode default to `analysis` and `either`.

An existing explicit ID updates declarative fields but preserves runtime status,
block reason, completion time, and active-round membership. Registration is
rejected atomically when it would create an invalid stage, missing dependency,
self-edge, duplicate input ID, or dependency cycle.
If all declarative fields and provenance are unchanged, registration is a no-op:
it does not rewrite the register, change timestamps, or append an event.

## 3. Selection

`advance` and `refine` consider only pending items with a compatible mode and
settled dependencies. A dependency is settled when it is `done` or explicitly
`dropped`; blocked and pending dependencies remain unsatisfied. Supplied
selectors match by tag or exact item ID using union semantics. With no selector,
all ready items in the earliest lifecycle stage are selected. Selection never
bypasses a dependency.

## 4. Exclusive round invariant

Starting a round creates `.harness/round.lock` with atomic exclusive creation.
Only one competing start can succeed. The lock is a logical lease and remains
after the starting process exits. It contains sufficient provisional data to
reconstruct a register write interrupted between lock acquisition and round
materialization.

The successful start then writes the round into the register, marks items active,
creates the work directory, and changes the lock phase from `provisional` to
`active`. Failure after lock creation intentionally retains the lock.

`resume` reconciles the lock, register, active items, and round templates; it
increments a resume counter without creating a new scientific round. If a crash
occurs after the register records a close but before lock removal, `resume`
idempotently completes the close record and releases the lock. `close` updates
item and round states, appends the close event, and removes the lock as its final
operation. Users and agents must not delete the lock to change modes.

## 5. Persistence

JSON register and lock rewrites use a same-directory temporary file, flush,
filesystem synchronization, and atomic replacement. Event and checkpoint
appends are flushed and synchronized. Each write is UTF-8 with LF newlines.

The register is validated before canonical replacement. Report files are derived
and may always be regenerated. `work/` is never summarized destructively.

## 6. State transitions

```text
pending ──start──> active ──close(no done)──> pending
   │                 │  └──block────────────> blocked
   ├──block────────> blocked ──reopen───────> pending
   ├──done─────────> done
   └──drop(reason)─> dropped
```

An item cannot become done while any dependency is neither done nor dropped.
Closing a round returns undeclared active items to pending, retains blocked
items, and completes only explicit `--done` items.

## 7. Reports

Bare `./h` is the recovery card: project state, macro progress, active round,
items, last checkpoint, exact next action, work directory, and blockers.
`report` is the human macro view. `report --json` is the low-token model API.
`report --write` regenerates `STATUS.md` and `NEXT.md`. Human, generated, and
JSON status views include the public formal-claim IDs, declarations, and earned
statuses from `formal/CLAIMS.json`.

Lifecycle progress excludes dropped items from its denominator and never weights
items by guessed effort. It is an orientation signal, not a schedule forecast.

## 8. Verification and security

Configured checks are arrays of arguments and execute without a shell. The
harness does not execute text parsed from `PLAN.md`. `doctor` validates schemas,
IDs, stages, modes, dependencies, cycles, lock/register agreement, event JSON,
and required template files.

The register does not establish scientific truth. Evidence and proof status are
governed by the control files under `research/` and by project-specific replay
gates.

## 9. Guarded local execution

`run` accepts one argument-array command and a working directory inside the
project. It rejects timeouts above 240 seconds, scheduling nice levels below 5,
and explicit background launch tokens. Before launch it exclusively creates
`.harness/compute.lock`; another run is rejected while the recorded controller
or child PID is alive. A stale lock is removed only after neither PID exists.

The child receives a scheduling nice level of at least 10 by default, common
numerical thread environment variables fixed at one, and a new process group.
On timeout the controller sends `SIGTERM` to that group, waits three seconds,
then sends `SIGKILL` if needed. Exit status is 124. Success, failure, timeout,
interruption, and launch failure are atomically recorded in
`.harness/runtime/last-run.json` and appended to a local runtime event log.

Configured checks use the same guarded path. Bare `./h` and `recover` report an
active/stale compute lock or an unresolved interrupted/timeout launch so a cut
off model does not need to infer whether computation remains in flight.

## 10. Formal-claim promotion registry

`formal/CLAIMS.json` has schema version 1 and a `claims` list. Claim IDs are
unique `C` identities already present in `research/CLAIM_INDEX.md`; target
versions must occur in `research/TARGET.md`; every registered declaration must
have a literal `#print axioms` entry in `Formal/Audit.lean`.

Statuses are monotonically stronger metadata assertions:

```text
KERNEL_CHECKED < TARGET_INSTANTIATED < STATEMENT_FAITHFUL < FORMALLY_PROVED
```

The required declaration links and claim-kind-specific initialization,
reachability, exterior-witness, and dependency-audit fields are normative in
`docs/LEAN_CLAIM_STANDARD.md` and enforced structurally by the project audit.
Registry acceptance does not establish that a named declaration proves what the
field claims; clean Lean compilation and independent semantic review remain
separate gates.
