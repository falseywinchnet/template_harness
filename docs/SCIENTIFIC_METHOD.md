# Scientific evidence protocol

The project register tracks work; it does not certify claims. This protocol
defines the minimum evidence language shared by experimental, computational,
and mathematical projects.

## Claim statuses

- `PROPOSED`: precise enough to test, not yet supported.
- `OBSERVED`: reproduced in recorded data or computation under stated conditions.
- `SUPPORTED`: survives declared tests and has a direct evidence boundary.
- `KERNEL_CHECKED`: a pinned formal system accepts the exact declaration and its
  axiom surface is recorded; target instantiation may still be open.
- `TARGET_INSTANTIATED`: helper assumptions are discharged for the actual public
  object and domain.
- `STATEMENT_FAITHFUL`: target equivalence, object identity, objective interior,
  and exact falsification interface have passed independent audit.
- `FORMALLY_PROVED`: a statement-faithful theorem passes all preceding gates,
  clean replay, and independent adversarial review.
- `REFUTED`: a preserved counterexample or valid test contradicts it.
- `SUPERSEDED`: retained historically but replaced by a named claim.
- `UNRESOLVED`: material gap remains visible.

No status is inferred from polished prose. A claim may have multiple independent
boundaries, and conflicting claims remain separate until resolved.

## Evidence boundaries

Every supported claim terminates at one or more of:

1. preserved external source with exact locator and provenance;
2. preserved dataset plus acquisition and transformation record;
3. replayable computation with environment and expected output;
4. formal theorem with exact declaration and axiom audit;
5. declared trusted assumption, instrument, or foundational axiom.

A URL alone is not preservation. A passing program proves only the property it
actually checks. A formal theorem proves only its elaborated statement.

## Required adversarial checks

For each critical claim, test:

- assumption provenance and independent satisfiability;
- object identity between the checked and published object;
- quantifier, branch, endpoint, degeneracy, and sign coverage;
- non-vacuity of premises and constructed witnesses;
- the exact source of strictness or effect size;
- predeclared counterexample and falsification conditions;
- sensitivity to data, implementation, and environment choices;
- statement fidelity in both directions against the public target.
- objective target interior from raw data, not a result-bearing subtype;
- initialization/direct membership independently of preservation or closure;
- equivalence to exclusion of the exact data-bearing counterexample schema;
- target-object identity through every representation and naming convention.

## Promotion rule

Advancement produces raw work. A later refinement round may promote a result
only after recording its precise claim, dependencies, evidence boundary,
limitations, and failed alternatives. The original round remains unchanged.

Computational promotion additionally requires the completed compute contract,
truthful classification as discovery/quick audit/full replay, resource and
environment records, canonical certificate or output, and an independent
verification interface. See `COMPUTE_DESIGN.md` and `PYTHON_COMPUTATION.md`.

## Publication rule

The paper contains no stronger claim than the audited index. The release manifest
names every result-bearing artifact and replay command. Independent reproduction
uses a clean environment. Historical releases are immutable and corrected by a
new revision.
