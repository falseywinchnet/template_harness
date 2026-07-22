# Lean axiom audit

- Lean toolchain: see `lean-toolchain`
- Lake version:
- mathlib tag and resolved commit: see `lakefile.toml` and release manifest
- Audit command: `./h run --cwd formal --label lean-audit -- lake env lean Formal/Audit.lean`
- Audit scope: selected target-facing surface / exhaustive exported surface
- Last clean result: not yet established for a project theorem

## Allowed foundation

Record the exact axiom names printed by Lean for exported project declarations.
Do not copy an expected list from another project.

```text
No project theorem has been exported.
```

## Template claim-contract infrastructure

The generic vocabulary is audited separately and is not a project result:

```text
Formal.ClaimContract.target_iff_no_counterexample:
  propext, Classical.choice, Quot.sound
Formal.ClaimContract.target_excludes_counterexample:
  no axioms
Formal.ClaimContract.target_of_no_counterexample:
  propext, Classical.choice, Quot.sound
Formal.ClaimContract.objectiveInterior_of_witness:
  no axioms
Formal.ClaimContract.reachable_in_target:
  no axioms
```

The equivalence and `target_of_no_counterexample` use classical contradiction
for the reverse implication. Projects that require a constructive boundary
should use `target_excludes_counterexample` for the forward direction or prove
decidability for their actual conclusion rather than silently importing this
classical step.

## Audited declarations

Add every target-facing declaration in the same change that exports it. Preserve
or hash the exact audit output at release.

For each public claim include its object-identity, domain-witness, objective
target-interior, initialization/instantiation, target, counterexample-equivalence,
and exact-order exterior-witness declarations where applicable. Auditing only a
generic conditional helper is insufficient.

## Forbidden trust

- custom mathematical axioms not declared in `research/TRUSTED_BASE.md`;
- `sorry`, `admit`, or generated equivalents;
- unsafe/runtime/foreign bridges used as proofs;
- external certificate results without an explicit statement bridge;
- native/runtime/foreign evaluation used as a proposition bridge;
- a target theorem whose key membership, sign, or correspondence survives only
  as an undischarged parameter.
