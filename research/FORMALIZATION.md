# Formalization and certification plan

Formalization is optional. Use it where statement ambiguity, proof depth,
symbolic algebra, numerical bounds, or reuse risk justifies its cost.

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

## Resource discipline

Prefer targeted checks while developing and one full build at the release gate.
Serialize expensive formal builds unless the toolchain is known to isolate them.
Do not increase timeouts or resource limits to conceal an unstructured proof.

## Acceptance

- clean build from a clean environment;
- no forbidden placeholders;
- exact target statement comparison;
- assumptions and axioms recorded;
- result-bearing output preserved in the evidence ledger.
