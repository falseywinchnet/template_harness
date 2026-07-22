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
constraints, evidence already on hand, and any required formal system. From the
answers Sol will:

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
  --deliverable "A reproducible paper and supporting artifacts"
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
cycles. `advance TAG...` and `refine TAG...` activate only dependency-ready
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
- `sources/` — lossless local evidence and provenance records.
- `paper/` — modular manuscript and release controls.
- `formal/` — optional reproducible Lean environment.
- `docs/` — bootstrap, operations, method, layout, and formal specification.

The normative behavior of the command and data model is specified in
`docs/SPECIFICATION.md`; operating procedures are in `docs/OPERATIONS.md`.

## Requirements

The harness itself uses only Python 3.11+ and the standard library. `tectonic`
is optional for PDF builds. Lean work requires `elan`/`lake`; the toolchain and
mathlib revision are pinned inside `formal/`.

Run the baseline gates with:

```sh
make test
```
