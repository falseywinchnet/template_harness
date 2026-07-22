# Local resource safety

This policy governs material local computation: Lean/Lake, SymPy, exact Python,
PDF builds, generators, verifiers, simulations, and full test suites. It exists
because a command can outlive an agent turn, a numerical library can create
threads invisibly, and several individually reasonable jobs can make a desktop
unresponsive. A requested memory limit is not an adequate safety mechanism: it
may be advisory, unsupported, inherited incorrectly, or applied to only one
process rather than its descendants.

## Invariants

1. Run one material local command at a time through `./h run`.
2. Every guarded run has lower scheduling priority (`nice` 10 by default), one
   thread for common numerical backends, and a maximum wall time of 240 seconds.
3. Never start a replacement because a tool returned a session or cell ID. That
   means the command is still running. Poll or inspect `./h run-status`.
4. Do not use `&`, `nohup`, `disown`, job-control `bg`, worker pools, or parallel
   Promise launches for material local work. Parallelism requires a separately
   measured, isolated execution environment and is not the template default.
5. A timeout is a design result, not an invitation to raise the limit and retry.

The 240-second bound applies to each local subtask, not necessarily the whole
research computation. Work that cannot fit must be split into checkpointed,
independently verifiable stages or moved to an explicitly provisioned remote
runner. Release replays may consist of many bounded stages; each stage must have
an identity, durable output, and a restart boundary.

## Guarded commands

```sh
./h run --label sympy-check -- env SYMPY_GROUND_TYPES=python python3 computations/check.py
./h run --cwd formal --label lean-target -- lake build Formal.Foo
./h run --cwd formal --label lean-audit -- lake env lean Formal/Audit.lean
./h run-status
```

The global `.harness/compute.lock` records the controller and child process IDs.
A second guarded run refuses to start while either is alive. The child is placed
in its own process group so a watchdog timeout terminates its descendants, waits
briefly, and then forcibly kills survivors. `.harness/runtime/last-run.json`
records status, elapsed time, exit code, limits, and the post-timeout process
audit. These runtime files are local recovery state and are not committed.
This lock is independent of `.harness/round.lock`: the latter preserves the one
active `ADVANCE`/`REFINE` research round across sessions, while the compute lock
prevents simultaneous material processes inside that round.

Commands such as `./h check`, `./h check --all`, `make test`, `make paper`, and
`make formal` already enter the guard for their material subprocesses. Invoke
them directly; do not wrap them in `./h run`, because nested guards correctly
refuse to bypass the one-process lock.

The runner forces these common hidden pools to one thread:
`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, and `BLIS_NUM_THREADS`.
This does not prove that every dependency is single-threaded; benchmark and
inspect any new backend before trusting it locally.

Do not put credentials or private tokens in command-line arguments because the
runtime record preserves the argument list. Pass secrets through an appropriate
credential store or environment mechanism and keep them out of logs.

## Timeout response

The watchdog returns exit code 124, records a process audit with command names
redacted to executable basenames, and releases the compute lock after the whole
process group is gone. Then:

1. Run `./h run-status` and read the recorded stage and elapsed time.
2. Inspect the audit. If another legitimate process was consuming the machine,
   wait or coordinate; do not launch a competing copy.
3. If contention is not the likely cause, refactor: reduce the instance, change
   representation, narrow the Lean target/import surface, split a stage, add a
   durable checkpoint, or replace broad symbolic normalization with an exact
   recurrence or sparse domain operation.
4. Record the failure and next experiment with `./h note`. The next run must test
   a changed hypothesis about cost, not merely repeat the timed-out command.

After an abrupt controller crash, `./h` reports an active or stale compute lock.
An active child must be allowed to finish or explicitly investigated. A later
guarded invocation can recover a stale lock only after both recorded processes
are confirmed dead.

## What the watchdog does not establish

Lower priority reduces interference; it does not cap memory. Single-thread
environment variables reduce common implicit parallelism; they do not constrain
an unknown library. The watchdog limits duration and cleans up descendants; it
does not make an intractable algorithm acceptable. Complexity estimates,
scale tests, sparse representations, and small independent verifiers remain the
primary controls described in `docs/COMPUTE_DESIGN.md`.
