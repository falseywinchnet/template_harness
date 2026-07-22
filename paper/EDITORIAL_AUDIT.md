# Editorial audit

Complete this after the manuscript map is frozen and again for every release
candidate. Record findings rather than checking boxes from memory. The normative
rules are in `../docs/PAPER_NARRATIVE.md` and `../docs/PDF_HOUSE_STYLE.md`.

## Artifact state

- Audit date:
- Auditor:
- Manuscript commit:
- Candidate version:
- State: draft / submitted immutable / released immutable / revision candidate
- Prior public artifact, tag, and digest if any:
- Intended audience and venue constraints:

## Public claim spine

Write the actual wording or a precise locator. These rows must describe the same
object, scope, strength, evidence status, and version.

| Position | Wording / locator | Claim IDs | Scope or evidence qualifier | Consistent? |
|---|---|---|---|---|
| Title | | | | pending |
| Abstract | | | | pending |
| Main theorem / primary result | | | | pending |
| Introduction contribution | | | | pending |
| Conclusion | | | | pending |
| Submission and release metadata | | | | pending |

## Section burden audit

Copy the active rows from `PAPER_MAP.md`. A section fails if its entry dependency
has not already appeared, its burden is mixed, or its exit state is not used.

| ID | Reader question | Entry dependencies | Burden | Exit state | Disposition |
|---|---|---|---|---|---|
| | | | | | pending |

Branches not required by the principal result or a necessary interpretation:

| Branch | Why present | Keep / supplement / cut | Decision |
|---|---|---|---|
| | | | pending |

## Claim and dependency pass

- [ ] Objects, populations, domains, assumptions, and quantifiers appear at
      first public use.
- [ ] The main result appears early and matches `research/CLAIM_INDEX.md`.
- [ ] Every denominator, inverse, logarithm, limit, coordinate, normalization,
      and strictness source is legal where used.
- [ ] Sampled, generic, confluent, asymptotic, or surrogate statements have an
      explicit bridge to the public target.
- [ ] Computation and formalization are described at the status they earned.
- [ ] Quick audit, full replay, independent verification, and generation are
      not conflated.
- [ ] Abstract and conclusion introduce no unindexed claim.

## Reader and rhetoric pass

- [ ] The exposition follows reader dependencies, not discovery chronology.
- [ ] Each section opens with its question or burden and closes with its usable
      consequence.
- [ ] Signposting states logical work rather than repeating the contents list.
- [ ] `Clearly`, `obviously`, `trivially`, promotional adjectives, and vague
      validation verbs have been justified, narrowed, or removed.
- [ ] Notation is defined before use and one symbol has one role.
- [ ] Each display is introduced and its consequence is stated.
- [ ] Every figure and table is necessary, cited, legible, and independently
      understandable from its caption.
- [ ] Limitations prevent concrete misreadings and do not hide assumptions.
- [ ] The conclusion restates rather than strengthens the result.

## Literature and attribution pass

- [ ] Every citation was checked against the source for the attributed claim.
- [ ] Contextual sources are distinguished from theorem dependencies.
- [ ] Directly adjacent objects, methods, positive results, and negative results
      are represented.
- [ ] Novelty language is backed by a dated search record.
- [ ] Independent discovery, public disclosure, certification, submission, and
      publication are not collapsed into one priority date.
- [ ] Authorship, contribution, funding, conflicts, and acknowledgments are
      approved rather than inferred.

## Revision decision

For a new draft write `initial draft`. Otherwise classify every material edit
as editorial, strengthened presentation, evidence upgrade, scope correction,
gap repair, claim change, or corrigendum/retraction.

| Location / claim | Change class | Earlier artifact remains valid? | Disclosure and version action |
|---|---|---|---|
| | | | |

- Decision: no public revision / new revision / corrigendum / retraction
- Reason:
- Earlier artifact preserved at:
- Required `REVISION_HISTORY.md` entry:

## Visual and release pass

- [ ] Log audit passes with no unresolved references or overfull boxes.
- [ ] Release-mode text audit contains no placeholders or private local paths.
- [ ] Every rendered page was inspected at reading and thumbnail scale.
- [ ] Title block, headings, displays, floats, captions, references, headers,
      footers, and final page are visually sound.
- [ ] PDF metadata, visible front matter, archive metadata, version, commit, tag,
      DOI, and digests agree.
- [ ] The source archive is minimal, deterministic, and rebuilds the reviewed
      PDF under the recorded environment.

## Findings ledger

| ID | Severity | Location | Exact problem | Required correction or test | Status |
|---|---|---|---|---|---|
| E001 | | | | | open |

Use `fatal`, `major`, `moderate`, or `minor`. Distinguish verified defects from
plausible concerns and open questions in the problem text.

## Adversarial summary

- Strongest accurate version of the paper's contribution:
- Strongest reviewer objection:
- What evidence would change the verdict:
- Release verdict: block / revise / ready
- Residual limitations disclosed in the manuscript:
