# Scientific Project Harness

This repository is a reusable operating system for taking a scientific idea
from an explicit hypothesis to a reproducible paper. It gives a human and an
AI collaborator named **Sol** the same small control plane: a typed project
register, exclusive research rounds, crash-safe checkpoints, lifecycle reports,
claim/evidence templates, an optional Lean workspace, and a publication tree.

It is distilled from a completed mathematical research project. None of that
project's mathematics, sources, proofs, claims, or results are included here.

The harness is deliberately not a lab notebook database, autonomous scientist,
reference manager, or universal theorem prover. It formalizes only the pieces
that become expensive when they are missing: scope, dependencies, modes, current
state, recovery, evidence boundaries, verification gates, and release identity.

## Start a new project with Sol

Create a repository from this template and open it in Codex. Then say:

> Sol, start a new scientific project in this repository.

`AGENTS.md` directs Sol to run `./h`, see that the repository is unbootstrapped,
and follow `docs/BOOTSTRAP.md`. Sol asks a short intake covering the research
question, initial hypothesis, falsification boundary, deliverable, audience,
constraints, evidence already on hand, any required formal system, and the
expected computational scale and resource limits. From the answers Sol will:

1. generate `PROJECT.md` as the frozen first charter;
2. tailor the lifecycle items in `PLAN.md`;
3. integrate every `P` item with `./h register PLAN.md`;
4. write the first macro progress report; and
5. open either an advancement or refinement round, never both.

To inspect the interview before using an agent:

```sh
./h bootstrap
```

To record a completed intake directly:

```sh
./h bootstrap \
  --title "Project title" \
  --question "The exact research question" \
  --hypothesis "The initial, revisable hypothesis" \
  --falsifier "What result would refute or materially weaken it" \
  --deliverable "A reproducible paper and supporting artifacts" \
  --interior "A raw admissible instance and its strict/nondegenerate result" \
  --containment "Object identity, initialization, preservation, and reachability, if applicable" \
  --compute "Expected scale, runtime/memory budget, and restart needs"
```

## The everyday loop

Bare `./h` prints a compact recovery card. It is the first command in every
session and usually replaces reading several status files.

```sh
./h                         # where are we?
./h advance theory          # open a boundary-pushing round by tag
./h note "Reduced to two cases" --next "Test the singular case"
./h close --summary "Reduction survives both cases" --done P007

./h refine evidence         # audit or integrate existing work
./h note "Claim C03 lacks an independent source" --next "Locate source"
./h close --summary "Evidence map corrected"
```

An atomic `.harness/round.lock` prevents a second `advance` or `refine` command
from opening while a round exists. The lock represents a logical research round,
not a long-running process, so it intentionally survives terminal exits, model
cutoffs, and crashes. Recovery is explicit:

```sh
./h recover
./h resume
```

The recovery card points to the round directory and its last exact next action.
The lock is removed only after a successful `close`; every earlier failure leaves
the recovery handle intact.

## Safe local computation

Material local commands go through the same small guard, whether they invoke
Lean, SymPy, Python, a PDF build, or a replay:

```sh
./h run --label exact-check -- env SYMPY_GROUND_TYPES=python python3 computations/check.py
./h run --cwd formal --label lean-target -- lake build Formal.Foo
./h run-status
```

The runner admits only one command at a time, lowers its scheduling priority,
limits common numerical backends to one thread, and kills the entire process
group after at most four minutes. A timeout triggers a small process audit and
requires a wait-or-refactor decision; it must not be answered by starting another
copy or raising the local limit. Tool output containing a session or cell ID
means the original command is still active. See `docs/RESOURCE_SAFETY.md`.

## Register project work by writing Markdown

`PLAN.md` is readable source text. Each task is one checkbox line:

```md
- [ ] P021 | Prove the stability lemma | stage=analysis | mode=advance | tags=core,lemma | depends=P007 | accept=Proof covers boundary cases
```

Then integrate it:

```sh
./h register PLAN.md
```

IDs may be omitted for new items; the parser assigns the next `P` identity.
Existing explicit IDs are updated without erasing their runtime status. The
register rejects unknown stages, missing dependencies, self-dependencies, and
cycles. Re-registering unchanged text performs no state write or event append.
`advance TAG...` and `refine TAG...` activate only dependency-ready
items whose declared mode is compatible. With no tag, the earliest ready stage
is selected.

Useful state commands:

```sh
./h report                 # full lifecycle report
./h report --json          # compact machine interface
./h report --write         # regenerate STATUS.md and NEXT.md
./h block P009 --reason "Dataset license unresolved"
./h reopen P009
./h done P009
./h drop P012 --reason "Formalization is not justified for this project"
./h doctor                 # structural integrity check
./h check                  # fast configured verification
./h check --all            # includes optional paper and Lean builds
```

## Engineering guides

The template includes the operational detail normally learned only after a
large project becomes expensive:

- `docs/COMPUTE_DESIGN.md` — representation-first algorithm design, complexity
  budgets, sparse arithmetic, interval covers, caching, and pivot conditions.
- `docs/PYTHON_COMPUTATION.md` — exact Python/SymPy practice, directed numerics,
  expression-swell control, generator/verifier separation, and manifests.
- `docs/LEAN_ENGINEERING.md` — module-DAG design, build ladder, import and tactic
  discipline, axiom auditing, statement fidelity, and performance budgets.
- `docs/LEAN_CLAIM_STANDARD.md` — the publication-grade boundary between kernel
  checking and proof: exact falsifiers, objective target interior, object
  identity, initialization versus preservation, and adversarial derivation audit.
- `docs/PDF_HOUSE_STYLE.md` — manuscript architecture, mathematical typography,
  metadata, accessibility, build/log gates, visual QA, and release packaging.
- `docs/RESOURCE_SAFETY.md` — exclusive lowered-priority execution, numerical
  thread limits, four-minute watchdog cleanup, and timeout recovery.

Start computational work by completing `computations/COMPUTE_PLAN.md`. This
forces the algorithm's scale, arithmetic, completeness, resource envelope, and
verification interface to be designed before an expensive implementation makes
those choices accidentally.

## Two modes, one boundary

- **Advance** creates new analysis, experiments, constructions, or proof work.
  Its complete raw record stays under `work/` even when the route fails.
- **Refine** audits, cites, reorganizes, verifies, integrates, or edits existing
  work. It does not silently create a new scientific line and call it review.

Separating them makes negative results legible and prevents a polished summary
from being mistaken for independent support. A later refinement round promotes
only what survives its acceptance and evidence gates.

## From hypothesis to publication

The default `P001`–`P020` plan spans ten stages:

```text
hypothesis → scope → sources → design → analysis → verification
           → writing → review → reproduction → publication
```

`STATUS.md` reports this whole arc, not just the active technical task.
`research/` carries the target contract, dependency graph, claim index, trusted
base, non-vacuity audit, and evidence ledger. `paper/` carries the manuscript
map, release manifest, revision history, metadata, and deterministic archive
builder. `formal/` is an optional pinned Lean 4/mathlib starter; it is dormant
unless the project's verification plan actually calls for formalization. Drop
optional items explicitly when they do not apply; a dropped dependency is
settled and remains visible in history.

## File map

- `PROJECT.md` — research charter and falsification boundary.
- `PLAN.md` — editable Markdown source for `P` items.
- `STATUS.md`, `NEXT.md` — generated macro and resume views.
- `.harness/` — canonical JSON register, configuration, and append-only events.
- `work/` — one durable directory per advancement or refinement round.
- `research/` — target, claims, dependencies, sources, and audit contracts.
- `computations/` — compute plans, benchmarks, and a canonical manifest example.
  It also contains an optional known-good SymPy baseline pin.
- `sources/` — lossless local evidence and provenance records.
- `paper/` — modular manuscript and release controls.
- `formal/` — optional reproducible Lean environment.
  Its generic claim-contract vocabulary makes containment and falsification
  obligations explicit without pretending to prove a project instance;
  `CLAIMS.json` prevents unsupported formal-status promotion.
- `docs/` — bootstrap, operations, method, layout, and formal specification.

The normative behavior of the command and data model is specified in
`docs/SPECIFICATION.md`; operating procedures are in `docs/OPERATIONS.md`.

## Requirements

The harness itself uses only Python 3.11+ and the standard library. Guarded
local execution requires a POSIX environment with `nice`, process groups,
signals, and `ps` (macOS and Linux). `tectonic` is optional for PDF builds. Lean
work requires `elan`/`lake`; the toolchain and mathlib revision are pinned inside
`formal/`.

Run the baseline gates with:

```sh
make test
```
