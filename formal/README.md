# Optional Lean 4 workspace

This starter is pinned to Lean `v4.32.0` and mathlib `v4.32.0`, matching the
known-good configuration from the source project at template creation. The
project may repin deliberately, but must record exact resolved revisions in its
release manifest.

The complete working rules are in `docs/LEAN_ENGINEERING.md` and the stricter
publication boundary in `docs/LEAN_CLAIM_STANDARD.md`. Keep
`AXIOMS.md`, `PERFORMANCE.md`, and `research/FORMALIZATION.md` synchronized with
the theorem-bearing source.

Install `elan`, then run:

```sh
./h run --cwd formal --label lean-update -- lake update
./h run --cwd formal --label lean-build -- lake build
./h run --cwd formal --label lean-audit -- lake env lean Formal/Audit.lean
```

During development, check the edited source, build its named Lake target, then
build at least one importer before trusting downstream results. At a release
gate, run the full `lake build` and `lake env lean Formal/Audit.lean` in the same
tree. From the repository root, `python3 scripts/audit_project.py` rejects Lean
placeholders, custom axioms/constants, and unsafe declarations after removing
comments.

Before adding proof work, complete `research/FORMALIZATION.md`. The public target
must be frozen independently of Lean. A checked theorem is accepted only when:

- its fully elaborated statement matches the public claim in both directions;
- its raw public object, objective target-interior witness, initialization, and
  exact counterexample interface are separate audited declarations;
- its assumptions are derived or named in the trusted base;
- no `sorry`, `admit`, undeclared axiom, or unsafe theorem bridge is present;
- `#print axioms` output is recorded for exported results;
- the build succeeds from a clean pinned environment.

`Formal/ClaimContract.lean` provides generic logical vocabulary only. Proving a
generic no-counterexample equivalence or reachability theorem does not establish
the project instance. The project-specific declaration chain belongs in
`research/FORMALIZATION.md` and `Formal/Audit.lean`.

Register each public formal claim and its earned status in `CLAIMS.json`. Empty
or inflated promotion metadata fails the project policy audit; the registry does
not replace compilation or semantic review.

Minimal first registration:

```json
{
  "claim_id": "C001",
  "kind": "universal",
  "target_version": "TARGET-v1",
  "declaration": "Formal.publicTheorem",
  "status": "KERNEL_CHECKED",
  "axiom_audit": ["propext", "Classical.choice", "Quot.sound"]
}
```

Use an empty `axiom_audit` list only when `#print axioms` actually reports none.
The additional fields required for promotion are specified in
`docs/LEAN_CLAIM_STANDARD.md`.

Prefer exact combinators and small named lemmas to large normalization tactics.
Do not hide a structural performance problem by raising heartbeats first. Record
per-module timings and any intentional limit change in `PERFORMANCE.md`. Do not
run concurrent Lean builds. Every local Lean/Lake invocation uses the global
guard and must finish within four minutes; split modules or move a bounded clean
replay to an isolated runner rather than weakening the local ceiling.
