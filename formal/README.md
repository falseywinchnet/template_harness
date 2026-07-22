# Optional Lean 4 workspace

This starter is pinned to Lean `v4.32.0` and mathlib `v4.32.0`, matching the
known-good configuration from the source project at template creation. The
project may repin deliberately, but must record exact resolved revisions in its
release manifest.

Install `elan`, then run:

```sh
cd formal
lake update
lake build
lake env lean Formal/Audit.lean
```

Before adding proof work, complete `research/FORMALIZATION.md`. The public target
must be frozen independently of Lean. A checked theorem is accepted only when:

- its fully elaborated statement matches the public claim in both directions;
- its assumptions are derived or named in the trusted base;
- no `sorry`, `admit`, undeclared axiom, or unsafe theorem bridge is present;
- `#print axioms` output is recorded for exported results;
- the build succeeds from a clean pinned environment.

Prefer one targeted module build during development and one full release build.
Do not run concurrent Lean builds in a constrained workspace.
