# Paper workspace

`manuscript/` contains a small modular LaTeX paper. `PAPER_MAP.md` maps sections
to claim and evidence burdens. `RELEASE_MANIFEST.md`, `REVISION_HISTORY.md`, and
`ARXIV_METADATA.md` control publication identity.

Project metadata lives in `manuscript/metadata.tex`, packages and semantic
macros in `manuscript/preamble.tex`, and the normative layout/release rules in
`../docs/PDF_HOUSE_STYLE.md`.

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
