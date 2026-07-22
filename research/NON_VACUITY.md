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

A successful implication checker is insufficient when its antecedent is
uninhabited, supplied as an unproved parameter, or detached from the public
object. Construct or identify target instances explicitly.
