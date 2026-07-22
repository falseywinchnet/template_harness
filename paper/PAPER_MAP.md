# Paper map

## Thesis

Replace with the exact primary claim from `research/TARGET.md`.

## Public claim spine

Copy the exact or shortened statement used at each public position. The object,
domain, quantifiers, strictness, evidence status, and version must agree.

| Position | Exact wording / source | Claim IDs | Scope or evidence qualifier |
|---|---|---|---|
| Title | | | |
| Abstract | | | |
| Principal theorem / result | | | |
| Introduction contribution | | | |
| Conclusion | | | |
| Release metadata | | | |

## Included sections

The map is an argument graph, not a table of contents. Each row has one reader
question, one burden, and an exit state later sections may consume.

| ID | File | Reader question | Entry dependencies | Scientific burden | Exit state | Claim IDs | Evidence class |
|---|---|---|---|---|---|---|---|
| `S00` | `sections/S00-abstract.tex` | What was decided, how, and within what boundary? | frozen claim index | Calibrated public contract | exact result and boundary | `C001` | audited index |
| `S01` | `sections/S01-introduction.tex` | What is the object, problem, contribution, and dependency path? | sources; target | State scope, main result, prior position, and architecture | reader knows the target and route | | sources |
| `S02` | `sections/S02-methods.tex` | What objects, assumptions, and methods make the result identifiable? | definitions; design | Define the scientific mechanism and acceptance gates | valid method inputs | | |
| `S03` | `sections/S03-results.tex` | What does the audited evidence establish? | methods; evidence | Present target-ordered results without inflation | supported result set | | |
| `S04` | `sections/S04-limitations.tex` | Where can this result fail or be misapplied? | results; falsification audit | State boundary cases, sensitivity, and limits | calibrated scope | | |
| `S05` | `sections/S05-reproducibility.tex` | How can the evidence and trust boundary be checked? | evidence ledger | State inputs, environment, commands, replay classes, and trust | reproducible verification contract | | ledger |
| `S06` | `sections/S06-conclusion.tex` | What exact claim survives, and what remains open? | results; limitations | Close the public claim spine without strengthening | final result and nearest open boundary | | |
| `S07` | `sections/S07-references.tex` | Which sources actually support or contextualize the argument? | citation audit | Identify used sources accurately | auditable attribution | | sources |

## Excluded and supplemental branches

Do not leave optional routes in the manuscript merely to describe them as
unused. Record the disposition so a later model does not reintroduce them.

| Branch | Relation to principal result | Disposition | Reason / artifact locator |
|---|---|---|---|
| | | cut / supplement / future paper | |

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
9. The title, abstract, principal result, introduction, conclusion, and release
   metadata remain one public claim spine.
10. Theory follows dependency order rather than discovery chronology. Tooling
    identity and artifact mechanics appear only where method or verification
    requires them.
11. `paper/EDITORIAL_AUDIT.md` records separate claim, dependency, reader, and
    release passes before publication.
12. Negative-style review removes performative contrasts, disclaimers, status
    declarations, stage directions, and figures of speech. Mathematical
    negations remain when they are themselves claims or proof conditions.
13. Computational artifacts and development provenance occur only in dedicated
    verification, reproducibility, availability, data, or software sections.
