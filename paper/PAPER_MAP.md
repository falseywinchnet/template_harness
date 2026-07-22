# Paper map

## Thesis

Replace with the exact primary claim from `research/TARGET.md`.

## Included sections

| ID | File | Scientific burden | Claim IDs | Evidence |
|---|---|---|---|---|
| `S00` | `sections/S00-abstract.tex` | Calibrated result and method summary | `C001` | audited index |
| `S01` | `sections/S01-introduction.tex` | Problem, scope, prior work, contributions | | sources |
| `S02` | `sections/S02-methods.tex` | Identifiable/replayable methods | | |
| `S03` | `sections/S03-results.tex` | Results without interpretive inflation | | |
| `S04` | `sections/S04-limitations.tex` | Falsification, sensitivity, and limits | | |
| `S05` | `sections/S05-reproducibility.tex` | Inputs, environment, commands, trust boundary | | ledger |
| `S06` | `sections/S06-conclusion.tex` | Exact conclusion and open boundary | | |
| `S07` | `sections/S07-references.tex` | Used sources | | |

## Editorial rules

1. The paper never exceeds the frozen claim index.
2. Methods and evidence are distinguished from interpretation.
3. Verification details are sufficient to reproduce but do not replace the
   scientific argument.
4. Optional or adjacent results cannot support the main chain backward.
5. `manuscript/metadata.tex` is the single source for PDF and release metadata.
6. Notation is semantic and stable; important equations and results are
   referenceable, while display math is not numbered decoratively.
7. Tables and figures state units, sample size, uncertainty, and provenance in
   their captions and remain legible without color.
8. The release PDF passes `scripts/audit_pdf.py` and a page-by-page rendered
   image inspection under `docs/PDF_HOUSE_STYLE.md`.
