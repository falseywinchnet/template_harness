# Lean axiom audit

- Lean toolchain: see `lean-toolchain`
- Lake version:
- mathlib tag and resolved commit: see `lakefile.toml` and release manifest
- Audit command: `lake env lean Formal/Audit.lean`
- Audit scope: selected target-facing surface / exhaustive exported surface
- Last clean result: not yet established for a project theorem

## Allowed foundation

Record the exact axiom names printed by Lean for exported project declarations.
Do not copy an expected list from another project.

```text
No project theorem has been exported.
```

## Audited declarations

Add every target-facing declaration in the same change that exports it. Preserve
or hash the exact audit output at release.

## Forbidden trust

- custom mathematical axioms not declared in `research/TRUSTED_BASE.md`;
- `sorry`, `admit`, or generated equivalents;
- unsafe/runtime/foreign bridges used as proofs;
- external certificate results without an explicit statement bridge.
