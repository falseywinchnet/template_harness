# Paper workspace

`manuscript/` contains a small modular LaTeX paper. `PAPER_MAP.md` maps sections
to claim and evidence burdens. `RELEASE_MANIFEST.md`, `REVISION_HISTORY.md`, and
`ARXIV_METADATA.md` control publication identity.

Build the PDF with:

```sh
make -C paper
```

This requires `tectonic`. Build the flattened, deterministic source archive with:

```sh
make -C paper archive
```

The archive builder expands local `\input` directives, strips comments, checks a
single document boundary, and writes `paper/release.tar` with a fixed timestamp.
Review the archive contents before submission; journal-specific extras must be
added intentionally and recorded in the release manifest.
