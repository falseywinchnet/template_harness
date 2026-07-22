# Paper workspace

`manuscript/` contains a small modular LaTeX paper. `PAPER_MAP.md` fixes the
public claim spine and maps every section to a reader question, entry
dependencies, one scientific burden, an exit state, claims, and evidence.
`EDITORIAL_AUDIT.md` supplies separate claim, dependency, reader, and release
passes. `RELEASE_MANIFEST.md`, `REVISION_HISTORY.md`, and `ARXIV_METADATA.md`
control publication identity.

Project metadata lives in `manuscript/metadata.tex`, packages and semantic
macros in `manuscript/preamble.tex`, and the normative layout/release rules in
`../docs/PDF_HOUSE_STYLE.md`. Argument order, rhetoric, and revision judgment
are governed by `../docs/PAPER_NARRATIVE.md`.

Before drafting, freeze the claim index and fill the thesis, public claim spine,
and section rows in `PAPER_MAP.md`. Draft in reader dependency order, not in the
order the work was discovered. Before a release, complete `EDITORIAL_AUDIT.md`
and classify every material post-submission edit in `REVISION_HISTORY.md`.

Build the PDF with:

```sh
./h run --cwd paper --label paper-build -- make
```

This requires `tectonic`. The build also audits unresolved references, overfull
boxes, embedded metadata, and font embedding when Poppler tools are available.
It does not replace visual inspection. Build the flattened, deterministic source
archive with:

```sh
./h run --cwd paper --label paper-archive -- make archive
```

The archive builder expands local `\input` directives, strips comments, checks a
single document boundary, and writes `paper/release.tar` with a fixed timestamp.
Review the archive contents before submission; journal-specific extras must be
added intentionally and recorded in the release manifest.

The normal build permits the template's instructional placeholders. A release
candidate must also pass the stricter extracted-text gate:

```sh
./h run --cwd paper --label paper-release-audit -- make release-audit
```

The release target first audits source prose for recurrent slop and misplaced
computational artifacts, then checks extracted PDF text for placeholders and
private local paths. During drafting, run the non-blocking report alone:

```sh
./h run --cwd paper --label manuscript-style -- make style-audit
```

It does not replace the semantic editorial audit or rendered page inspection.
