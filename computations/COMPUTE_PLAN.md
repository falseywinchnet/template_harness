# Computation plan — ID and short name

## Scientific contract

- Claim/obligation IDs:
- Exact proposition checked:
- Canonical inputs and domain:
- Counterexample or failure condition:
- Theorem/claim bridge:
- Discovery, quick audit, full replay, or release verification:

## Arithmetic and trust

- Exact/directed/statistical/diagnostic values:
- Arithmetic types and backend:
- Precision and rounding model:
- External libraries in the trusted base:
- Generator/verifier separation:

## Representation

- Symmetry and coordinate reductions:
- Forced factors/zeros/denominators exposed first:
- Sparse/dense/block/series representation:
- Shared dependencies that must remain correlated:
- Boundary/collision/separated regimes:

## Complexity budget

- Dimensions and parameter cases:
- Degree/order/matrix size:
- Estimated term/cell count and coefficient bit growth:
- Expected asymptotic time and memory:
- Wall-time and peak-memory budget:
- Checkpoint interval and resumability:
- Cache keys and invalidation rule:
- Small scale test and stop threshold:

## Completeness

- Finite-domain cover argument:
- Unbounded-domain analytic reduction:
- Adaptive termination/subdivision limit:
- Meaning of undecided or exhausted budget:

## Verification

- Independent direct formulation for small cases:
- Exact edge and degenerate fixtures:
- Fixed seed for diagnostic randomized checks:
- Canonical manifest schema:
- Expected stable final predicate:
- Corruption and incompleteness tests:

## Performance baseline

| Commit | Machine | Cache | Input scale | Time | Peak memory | Terms/cells | Result |
|---|---|---|---:|---:|---:|---:|---|
| | | cold/warm | | | | | |

## Pivot conditions

State when to stop rather than spend more precision, memory, or subdivisions.
