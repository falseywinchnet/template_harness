# Bootstrap protocol for Sol

The bootstrap converts an underspecified research idea into the smallest honest
project contract. It is complete when the user can recognize what will be done,
what will not be claimed, what can falsify the direction, and what artifact will
be delivered.

## 1. Inspect before asking

Run:

```sh
./h
./h bootstrap
```

If the repository already contains user materials, inventory filenames and
formats without interpreting them as established results. Do not browse or
acquire sources unless the user asks or the project cannot be scoped without
current information.

## 2. Ask one compact intake

Ask for:

1. project title and scientific field;
2. the exact research question;
3. the initial hypothesis, if any;
4. an observation that would refute or materially weaken it;
5. deliverable and intended audience;
6. deadline, constraints, non-goals, and required methods;
7. existing datasets, sources, code, proofs, or drafts and their locations;
8. whether formal proof, certified computation, independent reproduction, or
   ordinary statistical verification is required.
9. expected data/parameter scale, available compute, runtime constraints, and
   whether long computations must resume after interruption.
10. one independently constructible target-domain instance, the result expected
    there, and what prevents it from being only a boundary/equality case;
11. expected model time and cost per round, verified context window, desired
    reserve before compaction, and any provider rate or funding constraint;
12. for containment/invariance claims, the source object, target region, and
    whether initialization, preservation, and reachability are each intended.

Do not require the user to know workflow vocabulary. Translate their answer
into the fields. Ask a follow-up only when ambiguity changes the target,
falsifier, deliverable, or authorization boundary.

## 3. Materialize the charter

Record the core answers with `./h bootstrap --title ... --question ...
--falsifier ... --deliverable ...` and the optional fields. This generates
`PROJECT.md` and changes the project from `bootstrap` to `active` only when all
four required fields exist.

Use `--compute` for the initial scale/resource answer. It is a planning bound,
not a promise that the first algorithm will meet it; material methods replace it
with measured entries in `computations/COMPUTE_PLAN.md` and `BENCHMARKS.md`.
Local material work is always decomposed into stages of at most 240 seconds and
run through `./h run`; read `docs/RESOURCE_SAFETY.md`. Available memory remains
a design input, not a promise that a process-level memory request will protect
the machine.

Use `--model-budget` for acceptable time/cost per round and `--context-reserve`
for the verified model window and manual-handoff threshold. Record measured
provider values rather than advertised maxima. Keep the default 30% action point
when no better measurement exists. Read `docs/CONTEXT_ECONOMY.md`; do not set an
absolute Codex auto-compaction threshold until the active model window is known.

Then edit the research control files:

- `research/TARGET.md`: exact public target and non-goals;
- `research/DEPENDENCIES.md`: first claim decomposition;
- `research/TRUSTED_BASE.md`: tools, datasets, axioms, and external assumptions;
- `research/CLAIM_INDEX.md`: initial claims and status;
- `sources/README.md`: known source inventory and acquisition state.

If Lean is selected, complete the falsification-normal-form, objective-interior,
and initialization sections of `research/TARGET.md` before theorem engineering.
Read `docs/LEAN_CLAIM_STANDARD.md`; do not let a generic conditional helper
become the de facto target.

## 4. Tailor and register work

Edit `PLAN.md`. Keep the ten-stage macro arc, but remove unjustified work and
split high-risk items until each acceptance gate is observable. Do not retain
formalization merely because the template provides Lean.

Run:

```sh
./h register PLAN.md
./h doctor
./h report --write
```

The register is now canonical. Later edits to `PLAN.md` are integrated by
running `register` again; runtime statuses are preserved.

## 5. Begin intentionally

Choose one mode:

- `advance` if the next action creates scientific content;
- `refine` if it scopes, audits, sources, integrates, verifies, or edits.

Open the first dependency-ready item by tag or ID. Immediately record the first
exact next action if it is not obvious from the acceptance gate.

## Bootstrap acceptance gate

- the question and falsifier are concrete;
- the falsifier contains actual admissible data and the target domain has an
  independent objective-interior witness or a named open obligation;
- containment projects distinguish object identity, initialization,
  preservation, and reachability;
- scope and non-goals prevent an inflated conclusion;
- deliverable, audience, and constraints are explicit;
- existing inputs are inventoried without being upgraded to evidence;
- every initial `P` item has a mode, stage, dependencies, tags, and acceptance;
- material computations have an initial scale/resource estimate and verification
  class, bounded stages, and timeout pivot rather than an implicit promise to
  optimize later;
- model rounds have a time/cost boundary, context reserve, and manual handoff
  rule;
- `./h doctor` passes and the macro report reflects the charter.
