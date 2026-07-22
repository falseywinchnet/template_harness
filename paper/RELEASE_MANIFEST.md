# Release manifest

## Release identity

- Repository:
- Commit:
- Tag:
- Version:
- Date:
- Archival identifier / DOI:
- Manuscript: `manuscript/main.tex`
- Generated PDF: `build/manuscript.pdf`
- Source archive: `release.tar`

## Reproduction

| Tier | Command | Environment | Expected result | Output digest | Status |
|---|---|---|---|---|---|
| Harness | `make test` | Python 3.11+ | all checks pass | | pending |
| Paper | `make -C paper` | Tectonic version | PDF created | | pending |
| Archive | `make -C paper archive` | Python 3.11+ | deterministic tar | | pending |
| Formal (optional) | `cd formal && lake build` | pinned files | clean build | | not selected |

## Replay classes and resources

| Class | Purpose | Command | Expected time | Peak memory | Precision / arithmetic | Parallelism |
|---|---|---|---|---|---|---|
| Quick audit | Check structure and a small exact witness | | | | | |
| Full replay | Regenerate every result-bearing artifact | | | | | |
| Independent verification | Verify certificates without the generator | | | | | |

If a full computation is intentionally expensive, say so before release. A
quick audit must never be described as regenerating results it only samples or
verifies.

## Result-bearing artifacts

List every dataset, script, model, proof file, certificate, figure source, and
table source that affects a published claim. Record a stable path and SHA-256.

## Trust and exclusions

- Allowed trusted base:
- Unresolved limitations disclosed in paper:
- Files deliberately excluded from the public package:
- Privacy, license, or access constraints:

## Freeze gate

- claim index frozen and matches manuscript;
- target-reachable dependencies closed or disclosed;
- independent reproduction complete;
- clean checkout builds required tiers;
- full replay records runtime, peak memory, arithmetic/precision, and platform;
- PDF log audit and page-by-page rendered visual inspection pass;
- PDF, archive, metadata, commit, tag, and archival identity agree.
