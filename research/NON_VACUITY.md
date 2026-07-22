# Non-vacuity and statement audit

Apply this checklist to every critical implication and exported result.

| Gate | Question | Evidence | Status |
|---|---|---|---|
| Premise inhabitation | Can the hypotheses hold simultaneously for an actual target instance? | | open |
| Assumption provenance | Is every hypothesis in the target or derived by a named dependency? | | open |
| Object identity | Is the checked object the object named in the target? | | open |
| Quantifier coverage | Are all populations, cases, branches, endpoints, and degeneracies covered? | | open |
| Strictness/effect source | What prevents equality, null effect, or identifiability failure? | | open |
| Counterexample interface | What concrete result refutes the claim, and which check excludes it? | | open |
| Direction fidelity | Does the checked statement imply the target and does the target instantiate the checked result? | | open |
| Objective target interior | Is a raw target instance constructed independently and proved to lie on the claimed side? | | open |
| Interior dependency independence | Does the interior proof avoid invoking the exported target it is auditing? | | open |
| Boundary exclusion | For a strict claim, what margin/nonzero fact prevents the witness and theorem from living only at equality? | | open |
| Initialization | Does the actual source object enter the target region, independently of any preservation/closure theorem? | | open |
| Falsifier equivalence | Is the exported target equivalent to exclusion of the exact data-bearing counterexample schema? | | open |
| Definition independence | Are the public object and admissibility predicate defined without storing the desired conclusion? | | open |

A successful implication checker is insufficient when its antecedent is
uninhabited, supplied as an unproved parameter, or detached from the public
object. Construct or identify target instances explicitly.

An existential witness must not be manufactured from a property-bearing
subtype. Record the raw term, its admissibility proof, and its result proof as
separate dependencies. For containment or invariance, audit initialization and
preservation separately; a sealed target region may contain none of the source
objects.
