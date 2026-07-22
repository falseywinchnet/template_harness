# Research rounds

Every advancement or refinement round receives one directory here. The harness
creates:

- `ROUND.md` — immutable identity, mode, items, and contract;
- `NOTES.md` — timestamped checkpoints;
- `NEXT.md` — exact resume actions;
- `RESULTS.md` — supported outputs and close summary;
- `FAILURES.md` — failed routes and counterexamples.

Add data, scripts, figures, derivations, and source excerpts inside the same
round when they are specific to that attempt. Do not overwrite an earlier round
with its later summary. Integration happens in a refinement round while the raw
record remains available.

Start rounds only through `./h advance` or `./h refine`; the global lock and
register are part of their meaning.
