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
| Paper | `./h run --cwd paper --label paper-build -- make` | Tectonic version | PDF created | | pending |
| Archive | `./h run --cwd paper --label paper-archive -- make archive` | Python 3.11+ | deterministic tar | | pending |
| Formal (optional) | `./h run --cwd formal --label lean-build -- lake build` | pinned files | clean build | | not selected |
| Formal audit (optional) | `./h run --cwd formal --label lean-audit -- lake env lean Formal/Audit.lean` | pinned files | declaration axiom surface printed | | not selected |

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
- public claim spine agrees across title, abstract, principal result,
  introduction, conclusion, and release metadata;
- every section has a reader question, entry dependencies, one burden, and an
  exit state in `PAPER_MAP.md`; non-load-bearing branches are cut or explicitly
  assigned to a supplement;
- `EDITORIAL_AUDIT.md` has separate claim, dependency, reader, literature,
  negative-style, revision, and release passes with no unresolved fatal or major
  finding;
- every formal claim has the status it actually earned: kernel checked, target
  instantiated, statement faithful, or formally proved;
- objective target-interior, object identity, exact falsifier equivalence, and
  initialization/preservation audit are included for formal claims;
- target-reachable dependencies closed or disclosed;
- independent reproduction complete;
- clean checkout builds required tiers;
- full replay records runtime, peak memory, arithmetic/precision, and platform;
- PDF log audit and page-by-page rendered visual inspection pass;
- release-mode extracted-text audit contains no placeholders or private local
  paths;
- strict source audit reports no prose slop or computational artifact outside a
  dedicated section;
- PDF, archive, metadata, commit, tag, and archival identity agree.
