# Lean performance ledger

Record cold and warm observations separately. Timings are tied to a commit,
machine, cache state, and touched module.

| Date | Commit | Command / target | Platform | Cache | Wall time | Peak RSS | Notes |
|---|---|---|---|---|---:|---:|---|
| | | `lake build` | | cold/warm | | | |
| | | `lake env lean Formal/Audit.lean` | | warm | | | |

## Import graph

- Slow-moving roots:
- Frequently edited leaves:
- Largest invalidation edges:
- Current slowest modules:

## Budget

- Targeted iteration budget:
- Incremental full-build budget:
- Clean release-build budget:
- Serialized-build policy:

When a module exceeds budget, inspect import depth, duplicated normalization,
generated term size, and mixed responsibilities before increasing resource
limits.
