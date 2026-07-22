# Computation benchmarks

Benchmarks are observations tied to a commit, machine, input, and cache state.
They are not timeless performance claims.

| Date | Commit | Command | Platform | Input | Backend/precision | Cache | Wall time | Peak RSS | Output size | Digest |
|---|---|---|---|---|---|---|---:|---:|---:|---|
| | | | | | | | | | | |

## Regression policy

- Maintain one quick benchmark for ordinary development and one release-scale
  benchmark.
- Investigate material changes in term count, cell count, bit growth, output
  digest, wall time, or memory.
- Compare optimized and reference implementations on exact small cases.
- Record a representation or algorithm change before adopting a new baseline.
- Never hide an exhausted/undecided run by reporting only accepted cells.
