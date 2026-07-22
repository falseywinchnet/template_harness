# Paper and PDF house style

This house style targets mathematical and computational scientific papers. It
is intentionally conservative: readable typography, stable structure, explicit
evidence boundaries, and a submission package that can be rebuilt and audited.
It governs the rendered document; `PAPER_NARRATIVE.md` governs argument order,
claim-calibrated rhetoric, and revision judgment.

## 1. Page and typography

- Use an explicit paper size and approximately one-inch margins unless the venue
  supplies a class file.
- Default to an 11-point text face for a standalone preprint.
- Load T1 font encoding and `microtype`; use scalable fonts throughout.
- Use black text on white. Color may distinguish figures but must not carry
  meaning alone.
- Use `hidelinks` or restrained accessible link styling; never colored boxes
  around every citation.
- Avoid manual negative spacing, forced line breaks, and page geometry hacks.
- Keep paragraph measure comfortable; move wide derivations to aligned displays,
  a landscape supplement, or a factored notation rather than shrinking type.
- Use a table of contents only when the paper is long or structurally complex
  enough that it improves navigation. Most short articles do not need one.
- Keep heading depth shallow. A run of one-paragraph subsections usually signals
  that the argument map, not the type scale, needs revision.

The template uses `letterpaper`, 11 pt, and one-inch margins. Change paper size
once, explicitly, when the venue requires it.

## 2. Metadata and front matter

The source must define and the PDF must embed:

- exact title;
- approved authors and affiliations;
- contact/ORCID where appropriate;
- revision or release date;
- subject and keywords.

The first page contains a calibrated abstract followed by keywords and, for
mathematics, classification codes when applicable. Do not infer authorship,
affiliation, funding, or venue metadata.

The title, abstract, principal result, introduction contribution statement,
conclusion, and release metadata form one public claim spine. They name the same
object, scope, strength, evidence status, and version. The abstract states the
object, exact primary result, main mechanism, material evidence boundary, and
most important limitation. It does not contain local paths, internal task IDs,
or claims stronger than the frozen index.

## 3. Source architecture

- Keep `main.tex` declarative: metadata, section order, appendices.
- Put packages and macros in `preamble.tex`.
- Put project metadata in `metadata.tex` so PDF metadata and visible title agree.
- Use one stable source file per scientific section.
- Give sections stable IDs in `paper/PAPER_MAP.md`; displayed numbering may move.
- Define notation once in the preamble and use semantic macros for recurring
  operators, sets, differentials, and references.
- Keep proof/evidence prose in the relevant section; keep implementation and
  release mechanics in reproducibility/availability sections.
- Let the dependency path determine section order. Discovery chronology,
  superseded proof routes, and optional branches stay outside the manuscript
  unless they have independent scientific value.
- Remove a non-load-bearing branch instead of adding prose that announces it is
  unused. A section must carry one reader question and one scientific burden in
  `paper/PAPER_MAP.md`.

The flattened submission must contain one document class, one document start,
one document end, and no unresolved local `\input` directives.

## 4. Mathematics

- Number equations by section when the paper has substantial displayed algebra.
- Label only equations that are referenced; use semantic labels such as
  `eq:tail-bound`, not `eq:17`.
- Refer with `\eqref`, `\secref`, or an equivalent semantic macro.
- Number theorem-like environments by section and share one counter.
- State every theorem with domains, assumptions, and strict/weak orientation.
- Give long proofs a one- or two-sentence strategy before local calculations;
  end with the exact consequence consumed later.
- Define symbols before use and keep glyphs visually distinct.
- Break long calculations at mathematically meaningful equalities; never let a
  display run beyond the text block.
- Use `\operatorname`, `\mathrm`, and a differential macro for upright semantic
  text in formulas.
- Put large certificate tables or routine expansions in appendices/supplements,
  while retaining the load-bearing statement and bridge in the main text.
- Introduce each display and state its consequence. A long correct calculation
  without its logical role is not finished exposition.
- Use notation to expose dependency and sign structure, not to compress several
  different objects into visually similar symbols.

## 5. Tables, figures, and algorithms

- Use `booktabs`; avoid vertical rules and dense boxed grids.
- Include units in headers, not repeated in every cell.
- Give every figure/table a self-contained caption and cite it in the text.
- Prefer vector PDF/SVG/EPS-compatible artwork for diagrams and plots; use high-
  resolution raster only for inherently raster data.
- Ensure labels remain readable at final print size.
- Use colorblind-safe palettes and a second encoding such as shape, line style,
  or direct labels.
- State data transformation, uncertainty, and sample size in the caption or a
  direct methods reference.
- State whether a visual is proof/evidence, a diagnostic, or an illustration.
  A plot cannot establish an unsampled sign and a table cannot turn an unchecked
  computation into a theorem.
- Typeset pseudocode only when it clarifies the scientific method; the executable
  replay remains the authority for implementation.

## 6. Prose and evidence boundary

Theory sections describe objects, hypotheses, mechanisms, and deductions.
Names of languages, proof assistants, scripts, hashes, repositories, commands,
internal IDs, model names, and development history are confined to dedicated
verification, reproducibility, availability, data, or software sections. When
implementation is itself the scientific method, the theory describes the
algorithm and acceptance criterion; the dedicated section identifies the
artifact.

- Mathematical/results sections contain definitions, methods, deductions, and
  interpretation.
- The reproducibility section names software, versions, trust, exact commands,
  full versus quick replay, and objective success criteria.
- The availability section names repository, commit/tag, archive/DOI, licenses,
  and restricted-data procedures.
- Limitations disclose unformalized bridges, model restrictions, sensitivity,
  undecided regions, and negative results.
- A certificate hash establishes identity/reproduction, not theoremhood; phrase
  it accordingly.
- Do not call sampled diagnostics, wrapper audits, or selected cells the full
  proof-producing computation.
- Use claim-calibrated verbs from `PAPER_NARRATIVE.md`: exact replay can
  `reproduce`, a directed enclosure can `certify`, and a diagnostic may only
  `indicate` or `suggest`.
- Do not advertise absent methods or discarded routes. State the route used and
  omit the rest.
- Delete performative contrasts, disclaimers, status declarations, authorial
  stage directions, reviewer-facing defenses, and figures of speech under the
  negative controls in `PAPER_NARRATIVE.md`.

## 7. Accessibility

- Use a logical heading order and native LaTeX lists/tables rather than visual
  spacing tricks.
- Provide descriptive captions and text discussion for every visual.
- Do not encode conclusions only by color or spatial position.
- Avoid image-only equations and scanned text.
- Check copy/paste and text extraction order.
- Supply alt text/tagging through the venue toolchain when supported; if the
  produced PDF is untagged, record that as a release limitation rather than
  claiming accessibility compliance.
- Confirm fonts are embedded and glyphs render correctly.

## 8. Build and log gate

The maintained build is:

```sh
./h run --cwd paper --label paper-build -- make
```

It must fail on compilation errors, unresolved references/citations, overfull
boxes, missing PDF, or missing visible metadata. Underfull boxes are reviewed;
they fail only when they produce visible defects. The audit script is a narrow
log/metadata check and does not replace rendering.

Build twice when the engine requires cross-reference convergence. The selected
engine and version belong in the release manifest.

## 9. Visual gate

For every release candidate:

1. render every PDF page to PNG at a readable resolution;
2. inspect title block, abstract, contents, section starts, equations, tables,
   figures, appendices, references, and final page;
3. check clipping, overlaps, widows/orphans, blank pages, tiny labels, broken
   glyphs, excessive whitespace, and inconsistent hierarchy;
4. inspect at 100% and thumbnail scale;
5. run `pdfinfo` and a text-extraction sanity check;
6. search source, log, flattened source, and extracted text for placeholders,
   local paths, internal tokens, and unresolved markers.

A successful TeX exit is not visual QA.

## 10. Release package

- Build the PDF and flattened source from the same commit.
- Make the source archive deterministic: canonical order, fixed timestamps and
  permissions, no hidden files, logs, build products, private data, or VCS
  metadata.
- List archive contents before submission.
- Record SHA-256 for source archive, PDF, result-bearing artifacts, and replay
  outputs.
- Confirm PDF title/author/subject metadata matches visible front matter and
  submission metadata.
- Preserve each public revision as an immutable tag/release; corrections create
  a new revision history entry.
- Classify material edits before revision as editorial, strengthened
  presentation, evidence upgrade, scope correction, gap repair, claim change,
  or corrigendum/retraction. Preserve and identify the earlier artifact.

The normal build performs structural PDF checks. Before release, run the
release-mode text gate as well:

```sh
./h run --cwd paper --label paper-release-audit -- make release-audit
```

It runs the strict source-style audit, then rejects placeholder language and
private local paths in extracted PDF text. It cannot judge scientific truth or
novel slop forms; complete `paper/EDITORIAL_AUDIT.md` for those boundaries.

## 11. Final PDF checklist

- zero unresolved reference/citation warnings;
- zero overfull boxes;
- reviewed underfull boxes;
- embedded metadata and fonts;
- consistent notation, theorem numbering, and cross-references;
- readable grayscale/color output;
- figures/tables cited and accessible;
- exact claims match `research/CLAIM_INDEX.md`;
- public claim spine and section burdens pass `paper/EDITORIAL_AUDIT.md`;
- negative source-style audit passes with computational artifacts confined to
  dedicated sections;
- reproducibility and availability sections are truthful;
- every page visually inspected;
- deterministic archive and release manifest agree.
