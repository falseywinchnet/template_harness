# Formalization and certification plan

Formalization is optional. Use it where statement ambiguity, proof depth,
symbolic algebra, numerical bounds, or reuse risk justifies its cost.
Follow `docs/LEAN_ENGINEERING.md`; this file records the project-specific
choices required by that guide.

Mirror each public claim and its earned promotion status in
`formal/CLAIMS.json`. The JSON registry is the low-token machine index; the
declarations and reasoning recorded here remain the semantic audit.

## Selected seam

- Claim IDs:
- Why this seam is high risk:
- What remains outside the formal boundary:

## Exact statement map

| Public claim | Exported declaration | Counterexample declaration | Assumption map | Two-way fidelity | Status |
|---|---|---|---|---|---|
| `C...` | | | | | planned |

## Required declaration chain

| Obligation | Lean declaration | Defined independently? | Evidence/status |
|---|---|---|---|
| Raw public-object construction | | | |
| Representation/object identity | | | |
| Admissible-domain witness | | | |
| Objective target-interior witness | | | |
| Strictness/nondegeneracy source | | | |
| Technical-assumption discharge | | | |
| Initialization/direct membership | | | |
| Preservation and reachability | | | |
| Exported target | | | |
| Target iff no exact counterexample | | | |
| Exterior witness for exact-order/failure claim | | | |

Write `not applicable` only with a mathematical reason. A generic theorem that
accepts the desired property as a parameter does not close the corresponding
row for the public object.

The objective-interior declaration must be target-independent; record its
transitive dependencies and confirm that the exported target is absent.

## Definition and interpretation audit

- Fully unfolded public Lean object:
- Published object and normalization convention:
- Equality theorem covering the complete domain:
- Definitions capable of hiding sign/branch/domain information:
- Subtypes or structures carrying result-bearing fields:
- Remaining semantic or naming boundary outside Lean:

## Adversarial derivation audit

- Independent reviewer:
- Concrete raw admissible instance constructed without the conclusion:
- Result after deleting initialization but retaining preservation:
- Exact negated conclusion and data-bearing counterexample:
- Boundary/equality cases:
- Stronger-assumption or weaker-conclusion drift found:
- Final status: `KERNEL_CHECKED` / `TARGET_INSTANTIATED` /
  `STATEMENT_FAITHFUL` / `FORMALLY_PROVED`

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
- objective target-interior witness from raw data;
- exact counterexample-normal-form equivalence;
- initialization/membership proved separately from preservation/closure;
- target-reachable definitions and object identity audited;
- assumptions and axioms recorded;
- independent adversarial derivation review;
- targeted and full builds stay inside the recorded performance budget;
- result-bearing output preserved in the evidence ledger.
