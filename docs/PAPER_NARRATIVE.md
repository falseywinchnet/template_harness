# Paper narrative and rhetoric standard

This document controls the scientific argument carried by the manuscript.
`PDF_HOUSE_STYLE.md` controls the rendered object. Neither replaces the claim
index, evidence ledger, source audit, or discipline-specific conventions.

The standard is deliberately narrow. It exists to prevent recurring failures:
a correct result hidden behind discovery chronology, a headline stronger than
its evidence, optional branches competing with the main theorem, computation
described more strongly than it runs, and revisions that erase the identity of
an earlier submission.

## 1. Freeze the public claim spine

Before drafting prose, write one exact sentence for each of these positions:

1. title claim or question;
2. abstract result;
3. principal theorem, estimand, or empirical conclusion;
4. introduction contribution statement;
5. conclusion statement;
6. release and citation metadata.

These statements form the **public claim spine**. They must name the same
object, domain, quantifiers, strictness, evidence status, and version. Later
positions may be shorter but may not strengthen an earlier one. If the primary
result is conditional, computational, asymptotic, sampled, or formally proved
only for a surrogate, that boundary appears at its first public statement.

The title is a locator, not an advertisement. Avoid `exact`, `global`, `sharp`,
`complete`, `optimal`, `first`, `universal`, and equivalent terms unless the
claim index records their precise meaning and the manuscript proves it. A
famous motivating problem must not displace the theorem actually proved.

## 2. Build reader order from dependency order

The paper is a scientific argument, not a diary of how the result was found.
Order material by what a skeptical reader must know next:

```text
object and question
    -> exact result and scope
    -> minimum definitions and prior work
    -> load-bearing inputs
    -> mechanism joining those inputs
    -> result and boundary cases
    -> limitations
    -> verification and availability
```

Discovery routes, failed abstractions, tooling migrations, and superseded proof
paths stay in `work/`, the revision history, or a supplement when they have
independent scientific value. Do not include a branch merely to say that it is
not used. If it does not support the target or explain a necessary boundary,
remove it from the document graph.

Every section in `paper/PAPER_MAP.md` has:

- a reader question;
- entry dependencies already established;
- one scientific burden;
- claim IDs and evidence class;
- an exit state the reader may rely on later.

A section without a unique burden is merged, moved to a supplement, or cut.
Displayed section order may change; stable section IDs and burdens do not drift
silently.

## 3. Abstract as a contract

The abstract answers, in this order when the field permits:

1. What exact object or population is studied?
2. What question is decided?
3. What is the strongest supported result, with scope?
4. What is the central mechanism or design?
5. What evidence or verification boundary materially qualifies the result?
6. What is the nearest important limitation, if omission would mislead?

Use no citation, acronym, symbol, adjective, or implementation detail that is
not needed to identify the contribution. A verification method is named only
when it changes how the result should be interpreted. The abstract must not say
that all calculations, cases, certificates, or algebra are exposed unless that
literal burden is satisfied.

After the manuscript is stable, audit each abstract clause against a theorem,
result table, or disclosed evidence boundary. An unsupported clause is narrowed
or deleted; it is not rescued by suggestive prose elsewhere.

## 4. Introduction as a funnel

The introduction moves from object to exact contribution without suspense:

1. define the problem in the vocabulary used by the theorem;
2. state why the problem matters at the scale actually addressed;
3. state the main result early and completely;
4. separate positive and negative inputs, or empirical and interpretive inputs;
5. give the proof or analysis architecture in dependency order;
6. locate the contribution against directly relevant prior work;
7. state boundaries that prevent a predictable misreading.

Prefer a displayed main theorem near the beginning for theorem-led papers. For
empirical papers, give the primary estimand, population, comparison, and
uncertainty convention equally early. Do not make the reader infer the result
from a list of contributions.

Road-map sentences state logical work: “Section 4 derives X from Y.” Avoid
tourism language such as “we delve into,” “we explore various,” or a paragraph
that merely repeats the table of contents.

## 5. Claim-calibrated verbs

Choose verbs from the evidence status, not from desired emphasis.

| Evidence state | Suitable language |
|---|---|
| Theorem or deductive result with closed premises | proves, establishes, implies |
| Exact or directed computation with proved bridge | certifies, encloses, verifies |
| Reproduction of a named artifact | reproduces, regenerates |
| Statistical estimate under a stated model | estimates, is associated with, rejects under |
| Diagnostic, sample, plot, or search | indicates, suggests, is consistent with |
| Heuristic or conjectural mechanism | motivates, predicts, conjectures |

`Check`, `validate`, `confirm`, and `independent` are incomplete without an
object and boundary. Say what was checked, against what, and whether the method
shares definitions, code, data, formulas, or runtime with the generator.

Avoid `clearly`, `obviously`, `trivially`, and `straightforward` where they hide
a domain, sign, orientation, convergence, or identifiability obligation. Use a
short reason instead. Avoid novelty and priority claims without a documented
literature search; distinguish independent discovery, public disclosure,
certification, submission, and publication dates.

### Paragraph and sentence design

Give each paragraph one job. Its first sentence names the object or question;
its middle supplies the reason, evidence, or derivation; its final sentence
states the consequence when that consequence is not already explicit. Begin a
nontrivial proof with its strategy, then follow dependency order.

Use `we` for choices and actions performed in the paper; use the mathematical or
empirical object as subject for facts and implications. Replace ambiguous `this`,
`it`, `the above`, and `the latter` when more than one antecedent is possible.
Keep domains, exceptions, and evidence qualifiers in short visible sentences
rather than burying them inside parentheses. Prefer parallel syntax for parallel
claims. Avoid promotional adverbs, stacked nominalizations, and repetitive “we
show / we prove” openings. Rhetorical polish must make the logic easier to see,
not make the result sound larger.

## 6. Expose the load-bearing transitions

Definitions precede use. The first public statement of a result includes its
domain, assumptions, quantifiers, and strict/weak orientation. A proof section
may suppress routine algebra, but it may not suppress the bridge that connects
an evidence artifact, limit, coordinate change, computation, or imported
theorem to the public object.

For each major transition ask:

- Is the source object identical to the target object?
- Is every denominator, logarithm, inverse, or coordinate legal here?
- Is the result proved on the actual range, or extended beyond it by rhetoric?
- Does a confluent, limiting, generic, or sampled statement reach arbitrary
  admissible instances?
- Are orientation, indexing, normalization, and endpoint signs explicit?
- Does the complete tail, missingness mechanism, or uncertainty set enter the
  proof, rather than an inspected subset?

Put a strictness source, counterexample, or boundary case near the result it
qualifies. Do not postpone a condition that changes the theorem to a limitations
section.

## 7. Separate theory, computation, and verification

Mathematical sections present objects, assumptions, lemmas, mechanisms, and
deductions. They do not narrate which model, language, proof assistant, or
failed script discovered them. If the scientific method itself is an algorithm
or computation, describe the algorithm and its mathematical acceptance
criterion there; implementation identity, commands, hashes, and trust belong
in verification or reproducibility.

Formalization and exact computation may support a paper in different ways:

- a proof assistant checks the proposition encoded and its dependency closure;
- a generator constructs candidate data or proof objects;
- a verifier checks a stated property of those objects;
- a quick audit may inspect only structure or selected cases;
- a full replay regenerates every result-bearing artifact.

The manuscript names these roles truthfully. It never uses “exact,” “directed,”
“full,” or “independent” to describe a wrapper that performs only a sampled or
shared-implementation audit. A formal theorem is not advertised as proving the
intended scientific claim until object identity, statement fidelity, and the
trusted base are disclosed.

## 8. Figures, tables, equations, and captions

Every visual must perform argumentative work: define an object, expose a
comparison, show a diagnostic, or report a result. Decorative visuals and
tables that merely transpose prose are removed.

A caption is intelligible without hunting through the text. It states:

- what is shown and on what domain or population;
- variables, units, transformations, and sample size when applicable;
- uncertainty or enclosure convention;
- whether the visual is proof/evidence, a diagnostic, or an illustration;
- the source artifact or direct methods reference.

A plot does not prove an unsampled sign, a table does not launder computation
into a theorem, and a diagram does not replace a dependency argument. Equations
are numbered only when later prose depends on them. After a display, state its
logical consequence instead of making the reader infer why it appeared.

## 9. Related work, novelty, and attribution

Related work is an argument about position, not a bibliography dump. For each
nearby source record:

- the object and theorem actually established;
- the method or definition inherited;
- the difference in domain, strength, evidence, or purpose;
- whether the current work depends on it or is merely contextual.

Read the cited source, not only a secondary description. Do not cite a paper as
support for a claim it merely mentions. Do not grant or deny priority from
venue prestige or indexing alone. If priority matters, record independently
verifiable dates and use neutral chronology. “To our knowledge” still requires
a search record and should be used sparingly.

## 10. Limitations and conclusion

Limitations identify the nearest ways the result could be misapplied or fail to
generalize: unproved bridges, restricted domains, model dependence, data access,
sensitivity, accessibility, or incomplete reproduction. They are neither a
generic disclaimer list nor a place to hide assumptions needed by the theorem.

The conclusion closes the public claim spine. It restates the exact result
without a stronger adjective, interpretation, or domain. Then it names the
nearest honest open boundary. It does not add new evidence, novelty claims, or
speculation that would have required analysis earlier.

## 11. Revision identity and change classes

A submitted or released artifact is immutable. Later work may justify a new
version, never a silent rewrite. Before editing, classify each proposed change:

| Class | Meaning | Required record |
|---|---|---|
| Editorial | Wording or layout; no scientific meaning changes | revision note |
| Strengthened presentation | Equivalent, shorter, or more explicit route | route and equivalence |
| Evidence upgrade | Same claim, stronger replay/formal/archival support | old and new evidence boundary |
| Scope correction | Intermediate statement narrowed to what is proved | locations and downstream audit |
| Gap repair | A missing justification is supplied | affected claim, impact, repair |
| Claim change | Result, domain, assumptions, or conclusion changes | new claim audit and version |
| Retraction/corrigendum | A public claim is false or materially misleading | explicit public correction |

A proof refinement does not automatically require a manuscript revision. Revise
when the public artifact is false, misleading, materially unreproducible, or
scientifically improved enough to warrant a new identified version. Preserve the
prior PDF, source, commit, tag, date, and digest. Never describe a real gap as
mere polish, and never imply that a cleaner proof invalidated a sound earlier
argument.

## 12. Model editing protocol

An AI collaborator edits the paper only after reading the claim index,
`PAPER_MAP.md`, current artifact state, and relevant evidence boundary. It then:

1. names the exact burden being changed;
2. classifies the change under Section 11;
3. edits the smallest connected set of sections;
4. checks title, abstract, main result, limitations, conclusion, metadata, and
   release records for collateral drift;
5. preserves author voice, approved authorship, and factual attribution;
6. rebuilds and visually inspects the complete paper.

The model does not perform a broad “polish” rewrite, fabricate citations or
venue requirements, turn its own derivation into historical fact, or insert a
new result into the abstract or conclusion before it enters the claim index.
When asked for rhetoric, it improves logical visibility and calibration before
sentence ornament.

## 13. Required editorial passes

Use `paper/EDITORIAL_AUDIT.md` for four separate passes:

1. **Claim pass:** public spine, definitions, quantifiers, verbs, limitations.
2. **Dependency pass:** section burdens, order, bridges, removable branches.
3. **Reader pass:** motivation, signposting, captions, notation, prose rhythm.
4. **Release pass:** revision identity, metadata, availability, rendered pages.

Do not combine these into one impressionistic reread. Record concrete findings,
locations, dispositions, and the final adversarial summary.

## 14. Decision heuristics recovered from practice

These are small rules with unusually high leverage:

- Audit literal behavior, not labels. If a command called `full`, `directed`, or
  `independent` does less, rename it before rewriting prose around it.
- Prefer a robust exact witness or margin to a cancellation-sensitive decimal
  example, even when the latter discovered the phenomenon first.
- Prove claims on the actual domain or coordinate image needed. Do not buy a
  stronger global statement with an unproved extension.
- Keep one target theorem or primary result on the critical manuscript path.
  Extra true results compete for attention and create new consistency surfaces.
- Treat the paper map as a stale-state detector. When a proof route changes,
  audit every title, abstract, section burden, provenance table, conclusion, and
  release identifier that depended on the old route.
- Formalization may reveal a gap, a scope overstatement, an equivalent shorter
  proof, or merely an assurance upgrade. These are different revision classes.
- Contextual literature is not a proof dependency. A manuscript can cite and
  compare a theorem without importing its trust into the current argument.
- Independence is about failure diversity, not the number of scripts. Shared
  formulas, libraries, data, generators, or definitions must be disclosed.
- Visual review is an evidence check. Literal spacing tokens, broken formulas,
  float drift, and metadata inconsistencies can survive clean compilation.
- Release identity is part of scientific rhetoric: a reader must know which
  immutable object the claims, commands, digests, and later corrections describe.
