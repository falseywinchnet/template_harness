# Formalization and certification plan

Formalization is optional. Use it where statement ambiguity, proof depth,
symbolic algebra, numerical bounds, or reuse risk justifies its cost.
Follow `docs/LEAN_ENGINEERING.md`; this file records the project-specific
choices required by that guide.

## Selected seam

- Claim IDs:
- Why this seam is high risk:
- What remains outside the formal boundary:

## Exact statement map

| Public claim | Formal declaration or certificate predicate | Assumption map | Two-way fidelity | Status |
|---|---|---|---|---|
| `C...` | | | | planned |

## Environment

- Toolchain and revision:
- Library and revision:
- Build command:
- Audit command:
- Allowed trusted axioms:
- Forbidden placeholders or unsafe bridges:

## Module and build design

- Slow, stable root modules:
- Frequently edited leaf modules:
- Certificate boundary and independent verifier:
- Targeted build command:
- Importer build command that refreshes `.olean` files:
- Full build plus audit command:
- Expected targeted/full runtime and memory ceiling:

## Resource discipline

Use the build ladder: source check, targeted module build, importer build,
same-tree full build, then the independent audit file. A direct `lake env lean`
check does not refresh downstream `.olean` files. Serialize Lean builds unless
the toolchain is known to isolate them. Profile before raising heartbeats or
resource limits; first narrow imports, reduce expansion, or split mixed modules.

## Acceptance

- clean build from a clean environment;
- no forbidden placeholders;
- exact target statement comparison;
- assumptions and axioms recorded;
- targeted and full builds stay inside the recorded performance budget;
- result-bearing output preserved in the evidence ledger.
